# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2 # type: ignore
import imutils
import time

from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
import moviepy.video.fx.all as vfx
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-vert", "--vertical", default=1, nargs='?',
    help="video orientation")
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")

ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
greenLower = (5, 163, 53)
greenUpper = (14,255,255)

# greenLower = (10, 100, 20)
# greenUpper = (25,255,255)

pts = deque(maxlen=args["buffer"])

laps = 0
counter = 0
(dX, dY) = (0, 0)
direction = ""
prevDirection = ""
laps = 0

if not args.get("video", False):
    vs = VideoStream(src=0).start()
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

time.sleep(2.0)
print(args["vertical"])
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    
    frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

    if frame is None:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 0:
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)

       
# loop over the set of tracked points
    for i in np.arange(1, len(pts)):

        if len(pts) < 11:
            continue
        if pts[i - 1] is None or pts[i] is None:
            continue

        if counter >= 10 and i == 1 and pts[-10] is not None:

            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
 
            if np.abs(dX) > 30 and args["vertical"]:
                direction = "East" if np.sign(dX) == 1 else "West"

            if np.abs(dY) > 20 and not args["vertical"]:
                direction = "North" if np.sign(dY) == 1 else "South"
     
            if prevDirection != direction:
                laps += 1
            prevDirection = direction

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    cv2.putText(frame, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 0, 255), 3)
    cv2.putText(frame, "dx: {}, dy: {}".format(dX, dY),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.35, (0, 0, 255), 1)
    cv2.putText(frame, str(laps), (100, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 0, 255), 3)
        
    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()
# otherwise, release the camera
else:
    vs.release()
# close all windows
cv2.destroyAllWindows()