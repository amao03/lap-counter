import cv2
import random
import imutils

def getRandomFrame(video):
  # get total number of frames
  totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
  print(totalFrames)
  randomFrameNumber = random.randint(0, totalFrames - 1)

  # set frame position
  video.set(cv2.CAP_PROP_POS_FRAMES, randomFrameNumber)
  success, image = video.read()
  image = imutils.resize(image, width=600)

  return image