import cv2
import random
import imutils
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

def getGoodRandomFrame(video, prompt, mainWindow, continueFunc):
  mainWindow.randomFrameTimer = QTimer()
  mainWindow.randomFrameTimer.timeout.connect(lambda: processFrame(video, prompt, mainWindow, continueFunc))
  mainWindow.randomFrameTimer.start(1000)

def processFrame(video, prompt, mainWindow, continueFunc):
  randomFrame = singleRandomFrame(video)
  mainWindow.showCV2Image(randomFrame)

  reply = QMessageBox.question(mainWindow, 'Confirmation', prompt, 
    QMessageBox.Yes | QMessageBox.No)
  
  if reply == QMessageBox.Yes:
    mainWindow.randomFrameTimer.stop()
    continueFunc(randomFrame, mainWindow)

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