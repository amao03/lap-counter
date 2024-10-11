# first crop just the water with color detection

# use color detection to detect area of water,
# then continue to check frames until find person in the water

import cv2
import numpy as np
from moviepy.editor import VideoFileClip


image = cv2.imread('results/random-frame.jpg')
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# searching for blue also blacks out the lane lines, so can focus on one lane
lower_blue = (89, 132, 113)
upper_blue = (212, 255, 218)

mask = cv2.inRange(hsv, lower_blue, upper_blue)
result = cv2.bitwise_and(image, image, mask=mask)

cv2.imshow('Original', image)
cv2.imshow('Result', result)

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("Image with Bounding Box", image)
else:
    cv2.destroyAllWindows()


video = VideoFileClip('../videos/horizontal-butterfly.mov')
vidWidth, vidHeight = video.size
print(w, h)
print(image.shape)
imageHeight, imageWidth, _ = image.shape

# convert image coordinates to video
croppedY = y * vidHeight / imageHeight
croppedHeight = h * vidHeight / imageHeight
croppedX = x * vidWidth / imageWidth
croppedWidth = w * vidWidth / imageWidth

cropped_clip = video.crop(x1=croppedX, y1=croppedY, x2=croppedX + croppedWidth, y2=croppedY + croppedHeight)
cropped_clip.write_videofile('cropped_video3.mp4')

cv2.waitKey(0)
cv2.destroyAllWindows()
