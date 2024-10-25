# functions to crop video and get hsv color

import cv2
import numpy as np
from moviepy.editor import VideoFileClip


def getCoordinatesByColor(image):
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

    return x, y, w, h

def getCoordinatesByUser(image):
    poolSelection = cv2.selectROI("Frame", image, fromCenter=False,
			showCrosshair=True)

    return int(poolSelection[0]), int(poolSelection[1]), int(poolSelection[2]), int(poolSelection[3])

x = 0
y = 0 
def getHSVByUser(image):
    cv2.imshow('image', image) 
    cv2.setMouseCallback('image', click_event)
    cv2.waitKey(0) 

    return get_hsv_value(image, x, y)


def get_hsv_value(image, x, y):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_value = hsv_image[y, x]

    lowerLimit = int(hsv_value[0]) - 10, 100, 100
    upperLimit = int(hsv_value[0]) + 10, 255, 255
    print(hsv_image)
    
    print("HSV value at pixel ({}, {}): {}".format(x, y, hsv_value))
    print(lowerLimit)
    print(upperLimit)
    
    return lowerLimit, upperLimit


# function to display the coordinates of 
# of the points clicked on the image  
def click_event(event, x, y, img, params): 

    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
  
        # displaying the coordinates 
        # on the Shell 
        print(x, ' ', y) 
        print(img)

        x = x
        y = y
  

def cropVideo(video, image, videoPath):
    x, y, w, h = getCoordinatesByUser(image)

    vidWidth, vidHeight = video.size
    imageHeight, imageWidth, _ = image.shape

    # convert image coordinates to video
    croppedY = y * vidHeight / imageHeight
    croppedHeight = h * vidHeight / imageHeight
    croppedX = x * vidWidth / imageWidth
    croppedWidth = w * vidWidth / imageWidth

    cropped_clip = video.crop(x1=croppedX, y1=croppedY, x2=croppedX + croppedWidth, y2=croppedY + croppedHeight)
    cropped_clip.write_videofile(videoPath + '-cropped.mp4')

# image = cv2.imread('results/swim-horizontal-frame.jpg')
# x, y, w, h = getCoordinatesByUser(image)


# video = VideoFileClip('../videos/horizontal-butterfly.mov')
# video = VideoFileClip('../videos/cropped-swim-horizontal.mp4')
# vidWidth, vidHeight = video.size
# print(w, h)
# print(image.shape)
# imageHeight, imageWidth, _ = image.shape

# convert image coordinates to video
# croppedY = y * vidHeight / imageHeight
# croppedHeight = h * vidHeight / imageHeight
# croppedX = x * vidWidth / imageWidth
# croppedWidth = w * vidWidth / imageWidth

# cropped_clip = video.crop(x1=croppedX, y1=croppedY, x2=croppedX + croppedWidth, y2=croppedY + croppedHeight)
# cropped_clip.write_videofile('cropped-video-above-im.mp4')

# cv2.waitKey(0)
# cv2.destroyAllWindows()
