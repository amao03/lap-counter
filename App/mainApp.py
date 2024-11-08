import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMenu, QAction, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtMultimediaWidgets import QVideoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        leftPanel = QVBoxLayout()
        middlePanel = QVBoxLayout()

        # define left panel
        self.setWindowTitle("Lap Counter")
        chooseFileButton = QPushButton("Choose Video")
        chooseFileButton.clicked.connect(self.openFileDialog)

        leftPanel.addWidget(chooseFileButton)

        # define middle panel
        video = QVideoWidget()
        label = QLabel("hello")
        middlePanel.addWidget(video)
        middlePanel.addWidget(label)

        layout.addLayout(leftPanel)
        layout.addLayout(middlePanel)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def openFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            fileName = fileName[:-4]
            print(fileName)


    # menu on right click
    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())


if __name__ == '__main__':
    app = QApplication(sys.argv) # or [] if no cmd line args
    window = MainWindow()
    window.show()
    app.exec()
