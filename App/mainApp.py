import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QStyle, QGraphicsItem, QApplication, QMainWindow, QPushButton, QMenu, QAction, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QStackedLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem, QShortcut
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QRectF, QSizeF, QPointF
from PyQt5.QtGui import QPixmap, QImage, QPen, QBrush, QKeySequence, QColor

from main import * 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lap Counter")
        self.setFixedWidth(1500)

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

        # self.playButton = QPushButton()
        # self.playButton.setEnabled(False)
        # self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        # self.playButton.clicked.connect(self.play)
        
        # stackedLayout.addWidget(self.imageWidget)
        # stackedLayout.addWidget(self.videoWidget)
        
        middlePanel.addWidget(chooseFileButton)
        middlePanel.addLayout(stackedLayout)
        # middlePanel.addWidget(self.playButton)

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

    def showCV2Image(self, image, clickable=False):
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(qImg)

        self.scene.clear()

        if clickable:
            self.qGraphicsPixmap = ClickablePixmap(pixmap, image, self)
            # self.view.setMouseTracking(True)
        else:
            self.qGraphicsPixmap = QGraphicsPixmapItem(pixmap)

        self.scene.addItem(self.qGraphicsPixmap)

    def showVideo(self, fileName):
        self.scene.clear()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.scene.addItem(self.videoWidget)

        # probably get rid of this since the videos automatically play
        # self.playButton.setEnabled(True)
    
    def selectROI(self):
        self.rectItem = ResizableRectItem(0, 0, 100, 100, self.qGraphicsPixmap)
        self.scene.addItem(self.rectItem)

    def keyPressEvent(self, event):
        if hasattr(self, "rectItem") and event.key() == Qt.Key_Return and self.rectItem in self.scene.items():
            x, y, w, h, imageWidth, imageHeight = self.rectItem.getCoordinates()
            # remove retcItem from scene
            cropVideoFromPyQt(x, y, w, h, self, imageWidth, imageHeight)
            getHSVFrame(self)
            


class ResizableRectItem(QGraphicsRectItem):
    HANDLE_SIZE = 8  # Size of the resize handles

    def __init__(self, x, y, width, height, pixmapItem, parent=None):
        super().__init__(x, y, width, height, parent)
        self.pixmap_item = pixmapItem
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.handles = []  # To store corner handles
        self.handle_selected = None  # Currently selected handle
        self._create_handles()

    def _create_handles(self):
        """Create corner handles for resizing."""
        for i in range(4):
            handle = QGraphicsEllipseItem(0, 0, self.HANDLE_SIZE, self.HANDLE_SIZE, self)
            handle.setBrush(QBrush(Qt.red))
            handle.setPen(QPen(Qt.black))
            handle.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)  # Keeps handles same size
            self.handles.append(handle)
        self._update_handle_positions()

    def _update_handle_positions(self):
        """Update the positions of the corner handles based on the rectangle."""
        rect = self.rect()
        self.handles[0].setPos(rect.topLeft() - QPointF(self.HANDLE_SIZE / 2, self.HANDLE_SIZE / 2))
        self.handles[1].setPos(rect.topRight() - QPointF(self.HANDLE_SIZE / 2, self.HANDLE_SIZE / 2))
        self.handles[2].setPos(rect.bottomRight() - QPointF(self.HANDLE_SIZE / 2, self.HANDLE_SIZE / 2))
        self.handles[3].setPos(rect.bottomLeft() - QPointF(self.HANDLE_SIZE / 2, self.HANDLE_SIZE / 2))

    def _constrain_to_pixmap(self, rect):
        """Ensure the rectangle stays within the pixmap bounds."""
        pixmap_rect = self.pixmap_item.sceneBoundingRect()  # Bounds of the pixmap
        if rect.left() < pixmap_rect.left():
            rect.setLeft(pixmap_rect.left())
        if rect.top() < pixmap_rect.top():
            rect.setTop(pixmap_rect.top())
        if rect.right() > pixmap_rect.right():
            rect.setRight(pixmap_rect.right())
        if rect.bottom() > pixmap_rect.bottom():
            rect.setBottom(pixmap_rect.bottom())
        return rect
    
    def hoverMoveEvent(self, event):
        """Change cursor shape when hovering near handles."""
        for handle in self.handles:
            if handle.contains(event.pos() - handle.pos()):
                self.setCursor(Qt.SizeAllCursor)
                return
        self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Detect if a handle is selected for resizing."""
        self.handle_selected = None
        for handle in self.handles:
            if handle.contains(event.pos() - handle.pos()):
                self.handle_selected = handle
                break
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Resize the rectangle if a handle is selected."""
        if self.handle_selected:
            rect = self.rect()
            new_pos = event.scenePos()
            index = self.handles.index(self.handle_selected)
            if index == 0:  # Top-left
                rect.setTopLeft(new_pos)
            elif index == 1:  # Top-right
                rect.setTopRight(new_pos)
            elif index == 2:  # Bottom-right
                rect.setBottomRight(new_pos)
            elif index == 3:  # Bottom-left
                rect.setBottomLeft(new_pos)

            rect = self._constrain_to_pixmap(rect)
            self.setRect(rect)
            self._update_handle_positions()

    def mouseReleaseEvent(self, event):
        """Deselect the handle when the mouse is released."""
        self.handle_selected = None
        super().mouseReleaseEvent(event)

    def getCoordinates(self):
        pixmap_rect = self.pixmap_item.boundingRect()
        return self.boundingRect().x(), self.boundingRect().y(), self.boundingRect().width(), self.boundingRect().height(), pixmap_rect.width(), pixmap_rect.height()

class ClickablePixmap(QGraphicsPixmapItem):
    def __init__(self, pixmap, cv2Image, mainWindow):
        super().__init__(pixmap)
        self.mainWindow = mainWindow
        self.cv2Image = cv2Image



    def mousePressEvent(self, event):
        print("mousepress")
        item_pos = event.pos()
        scene_pos = event.scenePos()


    
    def mouseReleaseEvent(self, event):
        print("mouse release")
        scene_pos = event.pos()
        item_pos = self.mapFromScene(scene_pos)
        item_x = item_pos.x()
        item_y = item_pos.y()

        greenLower, greenUpper = get_hsv_value(self.cv2Image, int(item_x), int(item_y))
        
        runCounter(self.mainWindow, greenLower, greenUpper)
        

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.resize(800,800)
    window.show()
    app.exec()
