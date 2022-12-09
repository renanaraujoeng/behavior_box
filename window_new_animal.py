from PyQt5 import QtCore
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QDateTimeEdit, QPushButton, QMessageBox
from PyQt5.uic import loadUi

from Database import Database
from ProjectObjects import Animal


class UiNewAnimalDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiNewAnimalDialog, self).__init__()
        loadUi("window_new_animal.ui", self)
        self.setWindowTitle("Add Animal")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Set Button Icon
        self.bt_add.setIcon(QIcon("images/add.png"))
        self.bt_cancel.setIcon(QIcon("images/baseline_cancel_white_24dp.png"))

        # Connect all buttons to functions
        self.txt_weight.setValidator(QDoubleValidator())
        self.bt_cancel.clicked.connect(self.close)
        self.bt_add.clicked.connect(self.bt_cmd_add)

        self.is_edit = 0
        self.animal = None
        self.database = Database()

    def closeEvent(self, a0):
        self.closed.emit()

    def bt_cmd_add(self):
        if self.is_edit:
            if self.test_fields_ok():
                self.animal.name = self.txt_name.text()
                self.animal.weight = float(self.txt_weight.text())
                self.animal.birth = self.date_time_birth.dateTime().toPyDateTime()
                try:
                    self.database.edit_animal(self.animal)
                    QMessageBox.information(self, "Success", "Animal was edited")
                    self.close()
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")
        else:
            if self.test_fields_ok():
                self.animal = Animal(0, self.txt_name.text(), float(self.txt_weight.text()),
                                     self.date_time_birth.dateTime().toPyDateTime())
                try:
                    self.database.insert_animal(self.animal)
                    QMessageBox.information(self, "Success", "Animal was inserted to database")
                    self.txt_name.setText("")
                    self.txt_weight.setText("")
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")

    # Test if all the fields are filled
    def test_fields_ok(self):
        if not self.txt_name.text():  # Test if name QLineEdit text is empty
            QMessageBox.warning(self, "Warning", "The name was not informed.")
            return 0
        elif not self.txt_weight.text():
            QMessageBox.warning(self, "Warning", "The weight was not informed.")
            return 0
        else:
            return 1

    def edit_animal(self, animal: Animal):
        self.is_edit = 1
        self.animal = animal
        # Change Labels to match Edit Screen
        self.setWindowTitle("Edit Animal")
        self.label.setText("Edit Animal")
        self.bt_add.setText("Edit")
        self.bt_add.setIcon(QIcon("images/edit.png"))
        self.bt_add.setStyleSheet("""QPushButton {
                                                background-color: rgb(254, 197, 30);
                                                border-radius: 5px;
                                                color: rgb(255,255,255);
                                            }
                                            QPushButton:hover {	
                                                background-color: rgb(220, 167, 30);
                                            }
                                            QPushButton:pressed {	
                                                background-color: rgb(254, 197, 30);
                                            }""")
        # Set Animal values to fields
        self.txt_name.setText(animal.name)
        self.txt_weight.setText(str(animal.weight))
        self.date_time_birth.setDateTime(QDateTime.fromString(animal.birth.strftime("%Y-%m-%d %H:%M:%S"),
                                                              "yyyy-MM-dd HH:mm:ss"))

