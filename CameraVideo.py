import time

import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel


class CameraVideo:

    # resource_created = QtCore.pyqtSignal(str)

    def __init__(self, *args):
        if len(args) == 0:
            self.is_created = False
            self.is_running = False
            self.camera_index = 0
        else:
            self.parent = args[0]
            self.camera_index = args[1]
            self.img_label = args[2]
            self.video_thread = ThreadVideo(self.parent, self.camera_index, self.img_label)
            self.is_created = True
            self.is_running = False
            self.output = None

    def begin_capture(self):
        self.video_thread.changePixmap.connect(self.set_image)
        self.video_thread.start()
        self.is_running = True

    def stop_capture(self):
        self.video_thread.set_active(False)
        self.video_thread.get_capture().release()
        self.video_thread.terminate()
        self.is_running = False
        # self.camera_close.emit()

    def begin_saving_video(self, filename):
        # date = datetime.datetime.now()
        # fourcc = cv2.VideoWriter_fourcc('F', 'M', 'P', '4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.output = cv2.VideoWriter(filename, fourcc, 30, (640, 480))
        self.video_thread.start_saving(self.output)

    def stop_saving_video(self):
        self.video_thread.stop_saving()
        time.sleep(0.2)
        self.output.release()
        # self.video_thread.set_active(False)
        # self.video_thread.get_capture().release()
        # self.video_thread.terminate()
        # self.video_thread = ThreadVideo(self.parent, self.camera_index, self.img_label)
        # self.video_thread.changePixmap.connect(self.set_image)
        # self.video_thread.start()

    def stopped_saving(self):
        self.output.release()

    # @QtCore.pyqtSlot(QImage)
    def set_image(self, image: QImage):
        self.img_label.setPixmap(QPixmap.fromImage(image))

    @staticmethod
    def return_camera_indexes():
        # checks the first 10 indexes.
        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                if cap.isOpened():
                    arr.append(index)
                    cap.release()
            index += 1
            i -= 1
        return arr


class ThreadVideo(QThread):

    changePixmap = QtCore.pyqtSignal(QImage)
    # finished_saving = QtCore.pyqtSignal()

    def __init__(self, parent, camera: int, label: QLabel):
        super().__init__(parent)
        self.camera = camera
        self.label = label
        self.cap = cv2.VideoCapture(self.camera)
        self.is_saving = False
        self.output = None
        self.is_active = True

    def run(self):
        self.cap = cv2.VideoCapture(self.camera)
        while self.is_active & self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(self.label.geometry().width(), self.label.geometry().height())
                self.changePixmap.emit(p)
                cv2.waitKey()
                if self.is_saving:
                    self.output.write(frame)

    def get_capture(self):
        return self.cap

    def set_active(self, status: bool):
        self.is_active = status

    def start_saving(self, output):
        self.output = output
        self.is_saving = True

    def stop_saving(self):
        self.is_saving = False
