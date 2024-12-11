# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
# from moviepy.editor import VideoFileClip

from warmer import *
from videoPreprocessing import *
from randomFrame import *

import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-vert", "--vertical", default=1, nargs='?',
    help="video orientation")
ap.add_argument("-v", "--video",
    help="path to the video file")
ap.add_argument("-w", "--warmer", default=1, nargs='?',
    help="make video warmer")
ap.add_argument("-c", "--crop", default=1, nargs='?',
    help="crop video")
ap.add_argument("-b", "--buffer", type=int, default=32,
    help="max buffer size")
args = vars(ap.parse_args())


greenLower = (25, 50, 50)
greenUpper = (32,255,255)


pts = deque(maxlen=args["buffer"])

laps = 0
counter = 0
(dX, dY) = (0, 0)
direction = ""
prevDirection = ""
laps = 0


# If no video param, use the live stream
if not args.get("video", False):
    vs = cv2.VideoCapture("rtsp://admin:@192.168.1.117/Preview_01_main")
else:
    videoName = args["video"]
    moviePyVideo = VideoFileClip(videoName+".mp4")

    vs = cv2.VideoCapture(videoName+".mp4")

    if not args["crop"]:
        randomFrame = getGoodRandomFrame(vs, "Is this image good for cropping?")
        cropVideo(moviePyVideo, randomFrame, videoName)
        print("done crop")
        videoName = videoName + "-cropped"
        print(videoName)


    if not args["warmer"]:
        filter_video = warm_video(videoName+".mp4", (videoName+"-warmer.mp4"), 30)
        print("done watmer")
        videoName = videoName + "-warmer"
        print("captured")

    vs = cv2.VideoCapture(videoName+".mp4")


# Get the HSV values from pixel user selects
ret, frame = vs.read()
greenLower, greenUpper = getHSVByUser(frame)
print(greenLower, greenUpper)

# vs = cv2.VideoCapture("rtsp://admin:cse454hik@192.168.1.119:554/Streaming/channels/101")
vs = cv2.VideoCapture(videoName+".mp4")
# vs = cv2.VideoCapture("rtsp://admin:@192.168.1.117/Preview_01_main")
# rtsp://admin:@192.168.1.117/Preview_01_main

time.sleep(2.0)

start_time = time.time()
prev_time = time.time()
foundFirstPoint = None

previousTime = 0
elapsedTime = 0

oldX = 0
oldY = 0

didStart = False

splits = []

while True:
    ret, frame = vs.read()

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

            if not foundFirstPoint:
                foundFirstPoint = center
                start_time = time.time()
                

            elapsedTime = time.time() - previousTime 

            # print(elapsedTime)
            if elapsedTime > 1:
                displacement = int(x) - oldX
                # print(oldX, x)
                speed = np.abs(displacement) / elapsedTime
                previousTime = time.time()
                print(speed)

            oldX = int(x)
            oldY = int(y)
    
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
                if laps == 0:
                    start_time = 0
                else:
                    splits.append(time.time() - prev_time)
                    print(time.time() - prev_time)

                laps += 1
                prev_time = time.time()

            prevDirection = direction

        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    cv2.putText(frame, "Laps: ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (0, 0, 255), 3)
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
    # vs.stop()
    exit()
# otherwise, release the camera
else:
    vs.release()
# close all windows
cv2.destroyAllWindows()
