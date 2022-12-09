from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import numpy as np
import cv2


class ThreadVideo2(QThread):
    signal = pyqtSignal(np.darray, int, int, bool)

    def __init__(self, parent: QWidget, index: int, cam_id: id, link: str) -> None:
        QThread.__init__(self, parent)
        self.parent = parent
        self.index = index
        self.cam_id = cam_id
        self.link = link
        self.w = 960
        self.h = 540
        self.capture_delay = 80

    def run(self) -> None:
        cap = cv2.VideoCapture(self.link)
        while cap.isOpened():
            ret, im = cap.read()
            if not ret: break
            im = cv2.resize(im, (self.w, self.h))
            self.signal.emit(im, self.index, self.cam_id, True)
            cv2.waitKey(self.capture_delay) & 0xFF
        im = np.zeros((self.h,self.w, 3), dtype=np.uint8)
        self.signal.emit(im, self.index, self.cam_id, False)
        cv2.waitKey(self.capture_delay) & 0xFF