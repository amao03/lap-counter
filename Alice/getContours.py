import cv2
import numpy as np

img = cv2.imread("../cap.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv,(10, 100, 20), (25, 255, 255) )

print(mask)
cv2.imshow("orange", mask)


# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# # mask of green (36,25,25) ~ (86, 255,255)
# mask = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))
# mask = cv2.inRange(hsv,(10, 100, 20), (25, 255, 255) )

# yellow = cv2.bitwise_and(img,img, mask= mask)    

# cv2.imshow('Image', yellow)
cv2.waitKey(0)
cv2.destroyAllWindowss()
