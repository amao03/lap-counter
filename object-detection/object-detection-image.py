# https://medium.com/@hastisutaria.ict19/object-detection-using-opencv-f94f61e88b23

import cv2
import matplotlib.pyplot as plt
from matplotlib import ft2font

#importing and using necessary files
config_file='extra-files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
frozen_model='extra-files/frozen_inference_graph.pb'
#Tenserflow object detection model
model = cv2.dnn_DetectionModel(frozen_model,config_file)

classLabels=[]
filename='extra-files/yolov3.txt'

with open(filename,'rt') as fpt:
  classLabels = fpt.read().rstrip('\n').split('\n')

print("Number of Classes")
print(len(classLabels))
print("Class labels")
print(classLabels)

#Model training
model.setInputSize(750,750) # size that object may be?
model.setInputScale(1.0/127.5)
model.setInputMean((127.5,127.5,127.5))
model.setInputSwapRB(True)

#reading image
img = cv2.imread('swim-sreenshot.jpg')
plt.imshow(img)


#converting image from BGR to RGB
plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))

#object detection
ClassIndex, confidence, bbox = model.detect(img, confThreshold=0.5)

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
    cv2.rectangle(img, boxes, (0, 255, 0), 3)
    cv2.putText(img, classLabels[ClassInd-1], (boxes[0]+10, boxes[1]+40), font, fontScale=font_scale, color=(0, 0, 255), thickness=3)

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

plt.show()
