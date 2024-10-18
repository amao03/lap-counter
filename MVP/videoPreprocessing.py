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

def getHSVByUser(image):
    capSelection = cv2.selectROI("Frame", image, fromCenter=False,
			showCrosshair=True)
    
    x,y,w,h = int(capSelection[0]), int(capSelection[1]), int(capSelection[2]), int(capSelection[3])
    roi = image[y:y+h, x:x+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h_min, s_min, v_min = np.percentile(hsv_roi,10, axis=(0, 1))
    h_max, s_max, v_max = np.percentile(hsv_roi, 90, axis=(0, 1))

    # Lower and upper HSV bounds
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])

    return lower_bound, upper_bound


def getHSV(image):
    isHSVSelected = False
    while not isHSVSelected:  
        height, width = image.shape[:2]
        # resized_image = cv2.resize(image, (int(width * 3), int(height * 3)),  interpolation=cv2.INTER_CUBIC)
        hsv_min, hsv_max = getHSVByUser(image)
        print(hsv_min, hsv_max)
        hsv_selection = cv2.inRange(image, hsv_min, hsv_max)
        cv2.imshow("cap selection", hsv_selection)
        cv2.waitKey(1)

        success = input("is this selection good (y/n)?")
        if success == "y":
            isHSVSelected = True
            return hsv_min, hsv_max

   

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
