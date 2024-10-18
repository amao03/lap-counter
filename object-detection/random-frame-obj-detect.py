# This file takes a random frame from the video and does automatic object detection

import cv2
import matplotlib.pyplot as plt
from matplotlib import ft2font
import numpy as np
import time
import random
import imutils

#importing and using necessary files
config_file='extra-files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
frozen_model='extra-files/frozen_inference_graph.pb'
#Tenserflow object detection model
model = cv2.dnn_DetectionModel(frozen_model,config_file)

classLabels=[]
filename='extra-files/yolov3.txt'

with open(filename,'rt') as fpt:
  classLabels = fpt.read().rstrip('\n').split('\n')


#Model training
model.setInputSize(750,750) # size that object may be?
model.setInputScale(1.0/127.5)
model.setInputMean((127.5,127.5,127.5))
model.setInputSwapRB(True)

# video = cv2.VideoCapture('../videos/horizontal-butterfly.mov')
video = cv2.VideoCapture('../videos/swim-horizontal-short.mp4')

# get total number of frames
totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
randomFrameNumber = random.randint(0, totalFrames)

# set frame position
video.set(cv2.CAP_PROP_POS_FRAMES, randomFrameNumber)
success, image = video.read()
image = imutils.resize(image, width=600)

plt.imshow(image)


#converting image from BGR to RGB
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

cv2.imwrite('results/swim-horizontal-frame.jpg', image)

#object detection
ClassIndex, confidence, bbox = model.detect(image, confThreshold=0.5)

#fetching accuracy
print(confidence)

#fetching object index
print(ClassIndex)

#fetching coordinates of boxes
print(bbox)

#plotting boxes
font_scale = 3
font = cv2.FONT_HERSHEY_PLAIN
for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
    cv2.rectangle(image, boxes, (0, 255, 0), 3)
    cv2.putText(image, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40), font, fontScale=font_scale, color=(0, 0, 255), thickness=3)

plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

plt.show()




    


