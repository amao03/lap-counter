import cv2
import random
import imutils

def getGoodRandomFrame(video, prompt):
  isGoodImage = False
  while not isGoodImage:
      cv2.destroyAllWindows()
      randomFrame = singleRandomFrame(video)
      cv2.imshow("random frame", randomFrame)
      cv2.waitKey(1)

      success = input(prompt +" (y/n)?")
      if success == "y":
          cv2.destroyAllWindows()
          return randomFrame
          

def singleRandomFrame(video):
  # get total number of frames
  totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
  print(totalFrames)
  randomFrameNumber = random.randint(0, int(totalFrames) - 1)

  # set frame position
  video.set(cv2.CAP_PROP_POS_FRAMES, randomFrameNumber)
  success, image = video.read()
  image = imutils.resize(image, width=600)

  return image