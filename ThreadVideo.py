import cv2

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel


class ThreadVideo(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent, camera: int, label: QLabel):
        super().__init__(parent)
        self.camera = camera
        self.label = label
        self.cap = cv2.VideoCapture(self.camera)

    def run(self):
        self.cap = cv2.VideoCapture(self.camera)
        while True:
            ret, frame = self.cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(self.label.geometry().width(), self.label.geometry().height())
                self.changePixmap.emit(p)

    def get_capture(self):
        return self.cap
