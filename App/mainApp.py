import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QStyle, QGraphicsItem, QApplication, QMainWindow, QPushButton, QMenu, QAction, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QStackedLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QRectF, QSizeF, QPointF
from PyQt5.QtGui import QPixmap, QImage, QPen, QBrush

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
        self.qGraphicsPixmap = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.qGraphicsPixmap)

    def showVideo(self, fileName):
        self.scene.clear()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.scene.addItem(self.videoWidget)

        # probably get rid of this since the videos automatically play
        self.playButton.setEnabled(True)
    
    def selectROI(self):
        self.scene.addItem(ResizableRectItem(0, 0, 100, 100, self.qGraphicsPixmap))


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
        else:
            super().mouseMoveEvent(event)
            rect = self.rect()
            rect = self._constrain_to_pixmap(rect)
            self.setRect(rect)

            # pixmap_rect = self.pixmap_item.sceneBoundingRect()  # Pixmap's bounds in scene coordinates
            # item_rect = self.sceneBoundingRect()  # This rectangle's bounds in scene coordinates
            # print(pixmap_rect)
            # print(item_rect)


            # Calculate movement deltas
            # delta = event.scenePos() - event.lastScenePos()
            # new_pos = self.pos()  + delta
            # print(delta)
            # print(new_pos)

            # # Constrain the new position
            # if new_pos.x() < pixmap_rect.left():
            #     delta.setX(pixmap_rect.left() - self.pos().x())
            # elif new_pos.x() + item_rect.width() > pixmap_rect.right():
            #     delta.setX(pixmap_rect.right() - (self.pos().x() + item_rect.width()))

            # if new_pos.y() < pixmap_rect.top():
            #     delta.setY(pixmap_rect.top() - self.pos().y())
            # elif new_pos.y() + item_rect.height() > pixmap_rect.bottom():
            #     delta.setY(pixmap_rect.bottom() - (self.pos().y() + item_rect.height()))

            # # Move the item by the constrained delta
            # self.moveBy(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        """Deselect the handle when the mouse is released."""
        self.handle_selected = None
        super().mouseReleaseEvent(event)

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Enter:
    #         print("Enter key pressed")

if __name__ == '__main__':
    app = QApplication(sys.argv) # or [] if no cmd line args
    window = MainWindow()
    window.resize(800,800)
    window.show()
    app.exec()
