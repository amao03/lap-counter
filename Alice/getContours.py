# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
greenLower = (10, 100, 20)
greenUpper = (25,255,255)
# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])

laps = 0
counter = 0
(dX, dY) = (0, 0)
direction = ""
prevDirection = ""
laps = 0
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
# allow the camera or video file to warm up
time.sleep(2.0)
# keep looping

firstLoop = False
firstFrame = None
while True:
    # grab the current frame

    frame = vs.read()
    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)

    if not firstLoop:
        firstLoop = True
        firstFrame = frame

    frame = cv2.absdiff(frame,firstFrame)


    # image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV) 
    # hsv_hue = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # # Adjust the hue, saturation, and value of the image 
    # # Adjusts the hue by multiplying it by 0.7 
    # # 
    # # Adjusts the saturation by multiplying it by 1.5 
    # hsv[:, :, 1] = hsv[:, :, 1] * 20
    # Adjusts the value by multiplying it by 0.5 
    # hsv[:, :, 2] = hsv[:, :, 2] * 0.5
    
    # Convert the image back to BGR color space 
    # frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    frame = cv2.convertScaleAbs(frame, alpha=2, beta=0)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[:, :, 0] = hsv[:, :, 0] * 0.3
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 0:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)

       
# loop over the set of tracked points
    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if len(pts) < 11:
            continue
        if pts[i - 1] is None or pts[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")
            # ensure there is significant movement in the
            # x-direction
            if np.abs(dX) > 20:
                direction = "East" if np.sign(dX) == 1 else "West"
            # ensure there is significant movement in the
            # y-direction
            # if np.abs(dY) > 20:
            #     dirY = "North" if np.sign(dY) == 1 else "South"
            # handle when both directions are non-empty
            # if dirX != "" and dirY != "":
            #     direction = "{}-{}".format(dirY, dirX)
            # # otherwise, only one direction is non-empty
            # else:
            # direction = dirX if dirX != "" else dirY
            if prevDirection != direction:
                laps += 1
            prevDirection = direction

    # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
    # show the movement deltas and the direction of movement on
    # the frame
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
