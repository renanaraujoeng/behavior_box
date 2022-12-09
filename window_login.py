from PyQt5.uic import loadUi
# from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
# from window_main_backup import UiVideoMainWindow
from window_arduino import UiArduinoDialog


# Class Connected to window_login.ui
class UiLoginDialog(QDialog):
    def __init__(self):
        super(UiLoginDialog, self).__init__()
        # Load Ui variables (All Widgets on Ui)
        loadUi("window_login.ui", self)
        # Connect button to command when clicked
        self.bt_open_video.clicked.connect(self.bt_cmd_open_video)
        self.bt_arduino.clicked.connect(self.bt_cmd_arduino)
        # Create new Window

    def bt_cmd_arduino(self):
        print("Open Arduino")
        # Close the current frame
        self.close()
        # Show new frame
        self.new_window = UiArduinoDialog()
        self.new_window.show()

    def bt_cmd_open_video(self):
        print("Button Clicked")
        # Close the current frame
        self.close()
        # Show new frame
        self.new_window = UiVideoMainWindow(self)
        self.new_window.show()
