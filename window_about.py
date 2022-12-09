from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class UiAboutDialog(QDialog):
    def __init__(self):
        super(UiAboutDialog, self).__init__()
        loadUi("window_about.ui", self)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon("images/icon.png"))
        self.lb_logo.setPixmap(QPixmap("images/logo.png"))
        self.lb_icon.setPixmap(QPixmap("images/icon100.png"))
