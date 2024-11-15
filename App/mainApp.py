import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QStyle, QApplication, QMainWindow, QPushButton, QMenu, QAction, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QStackedLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap, QImage

from main import * 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lap Counter")

        layout = QHBoxLayout()
        #leftPanel = QVBoxLayout()
        middlePanel = QVBoxLayout()

        # define left panel
        # self.setWindowTitle("Lap Counter")
        # chooseFileButton = QPushButton("Choose Video")
        # chooseFileButton.clicked.connect(self.openFileDialog)

        # leftPanel.addWidget(chooseFileButton)

        # define middle panel
        chooseFileButton = QPushButton("Choose Video")
        chooseFileButton.clicked.connect(self.openFileDialog)

        stackedLayout = QStackedLayout()

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        stackedLayout.addWidget(self.view)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QGraphicsVideoItem()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        # stackedLayout.addWidget(self.imageWidget)
        # stackedLayout.addWidget(self.videoWidget)
        
        middlePanel.addWidget(chooseFileButton)
        middlePanel.addLayout(stackedLayout)
        middlePanel.addWidget(self.playButton)

        #layout.addLayout(leftPanel)
        layout.addLayout(middlePanel)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        # set up media player
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        #self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
       # self.mediaPlayer.positionChanged.connect(self.positionChanged)
        #self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","MP4 Files (*.mp4)", options=options)
        if fileName:
            # self.showVideo(fileName)
            fileName = fileName[:-4]
            self.fileName = fileName
            getCroppingFrame(fileName, self)
        

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            print("play")
            self.mediaPlayer.play()

    def showImage(self, fileName):
        self.scene.clear()
        image = QPixmap(fileName)
        self.scene.addItem(QGraphicsPixmapItem(image))

    def showCV2Image(self, image):
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(qImg)

        self.scene.clear()
        self.scene.addItem(QGraphicsPixmapItem(pixmap))

    def showVideo(self, fileName):
        self.scene.clear()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.scene.addItem(self.videoWidget)

        # probably get rid of this since the videos automatically play
        self.playButton.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv) # or [] if no cmd line args
    window = MainWindow()
    window.resize(800,800)
    window.show()
    app.exec()
