from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import QDialog, QComboBox, QTableWidget, QLineEdit, QMessageBox
from PyQt5.uic import loadUi

from Database import Database
from ProjectObjects import TrainingProgram, Discrimination


class UiNewProgramDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiNewProgramDialog, self).__init__()
        loadUi("window_new_program.ui", self)
        self.setWindowTitle("Add Training Program")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Set Button Icon
        self.bt_add.setIcon(QIcon("images/add.png"))
        self.bt_cancel.setIcon(QIcon("images/baseline_cancel_white_24dp.png"))
        self.bt_add_row.setIcon(QIcon("images/add.png"))
        self.bt_remove_row.setIcon(QIcon("images/remove.png"))

        # Connect all buttons to functions and set validators
        self.txt_max_rewards.setValidator(QIntValidator())
        self.txt_reward_ms.setValidator(QIntValidator())
        self.bt_cancel.clicked.connect(self.close)
        self.bt_add.clicked.connect(self.bt_cmd_add)
        self.bt_add_row.clicked.connect(self.bt_cmd_add_row)
        self.bt_remove_row.clicked.connect(self.bt_cmd_remove_row)

        # Initiate Table
        # self.table_disc = QTableWidget()
        self.table_disc.setColumnCount(3)
        self.table_disc.setHorizontalHeaderLabels(["Discrimination Type", "Nose Success", "Time (s)"])
        self.table_disc.setColumnWidth(0, 200)
        self.table_disc.setColumnWidth(1, 200)
        self.table_disc.setColumnWidth(2, 150)
        self.bt_cmd_add_row()

        self.is_edit = 0
        self.program = None
        self.database = Database()

    def closeEvent(self, a0):
        self.closed.emit()  # Send signal to other window that this one is closing

    def bt_cmd_add(self):
        if self.test_fields_ok():
            if self.is_edit:
                # Get the Discrimination List from table
                list_disc = []
                for row in range(self.table_disc.rowCount()):
                    disc_type = self.table_disc.cellWidget(row, 0).currentIndex()
                    nose_success = self.table_disc.cellWidget(row, 1).currentIndex()
                    time_sec = int(self.table_disc.cellWidget(row, 2).text())
                    disc = Discrimination(0, disc_type, nose_success, time_sec)
                    list_disc.append(disc)
                self.program.name = self.txt_name.text()
                self.program.max_rewards = int(self.txt_max_rewards.text())
                self.program.reward_ms = int(self.txt_reward_ms.text())
                self.program.total_time = int(self.txt_total_time.text())
                self.program.disc_list = list_disc
                try:
                    self.database.edit_program(self.program)
                    QMessageBox.information(self, "Success", "Training Program was edited")
                    self.close()
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")
            else:
                # Get the Discrimination List from table
                list_disc = []
                for row in range(self.table_disc.rowCount()):
                    disc_type = self.table_disc.cellWidget(row, 0).currentIndex()
                    nose_success = self.table_disc.cellWidget(row, 1).currentIndex()
                    time_sec = int(self.table_disc.cellWidget(row, 2).text())
                    disc = Discrimination(0, disc_type, nose_success, time_sec)
                    list_disc.append(disc)
                self.program = TrainingProgram(0, self.txt_name.text(), int(self.txt_max_rewards.text()),
                                               int(self.txt_reward_ms.text()), int(self.txt_total_time.text()),
                                               list_disc)
                try:
                    self.database.insert_program(self.program)
                    QMessageBox.information(self, "Success", "Training Program was inserted to database")
                    self.txt_name.setText("")
                    self.txt_max_rewards.setText("0")
                    self.txt_reward_ms.setText("20")
                    while self.table_disc.rowCount() > 0:
                        self.table_disc.removeRow(0)
                    self.bt_cmd_add_row()
                    self.calculate_total_time()
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")

    def bt_cmd_add_row(self):
        row_count = self.table_disc.rowCount()
        self.table_disc.setRowCount(row_count + 1)

        # Initiate Cell Widgets
        combo_disc_type = ComboDiscType(self.table_disc)
        combo_disc_type.activated[int].connect(self.cb_cmd_combo_box)
        combo_nose_success = ComboNoseSuccess(self.table_disc)
        txt_time = NumberLineEdit(self.table_disc)
        # txt_time.textChanged[str].connect(self.calculate_total_time())
        self.table_disc.setCellWidget(row_count, 0, combo_disc_type)
        self.table_disc.setCellWidget(row_count, 1, combo_nose_success)
        self.table_disc.setCellWidget(row_count, 2, txt_time)
        self.table_disc.cellWidget(row_count, 2).textChanged[str].connect(self.calculate_total_time)

    def bt_cmd_remove_row(self):
        row_selected = self.table_disc.currentRow()
        self.table_disc.removeRow(row_selected)
        self.calculate_total_time()

    def test_fields_ok(self):
        if not self.txt_name.text():
            QMessageBox.warning(self, "Warning", "The name was not informed.")
            return 0
        if not self.txt_max_rewards.text():
            QMessageBox.warning(self, "Warning", "The max number of rewards was not informed")
            return 0
        if not self.txt_reward_ms.text():
            QMessageBox.warning(self, "Warning", "The reward time (ms) was not informed.")
            return 0
        if self.table_disc.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Complete the table or remove empty rows")
            return 0
        for row in range(self.table_disc.rowCount()):
            if not self.table_disc.cellWidget(row, 2).text():
                QMessageBox.warning(self, "Warning", "Complete the table or remove empty rows")
                return 0
        return 1

    def edit_program(self, program: TrainingProgram):
        self.is_edit = 1
        self.program = program
        # Change labels to match edit window
        self.setWindowTitle("Edit Training Program")
        self.label.setText("Edit Training Program")
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
        # Set Training Program Values
        self.txt_name.setText(program.name)
        self.txt_max_rewards.setText(str(program.max_rewards))
        self.txt_reward_ms.setText(str(program.reward_ms))
        self.table_disc.removeRow(0)
        for disc in self.program.disc_list:
            self.add_disc_row(disc)
        self.calculate_total_time()

    def add_disc_row(self, disc: Discrimination):
        row_count = self.table_disc.rowCount()
        self.table_disc.setRowCount(row_count + 1)

        # Initiate Cell Widgets
        combo_disc_type = ComboDiscType(self.table_disc)
        combo_disc_type.setCurrentIndex(disc.disc_type)
        combo_disc_type.activated[int].connect(self.cb_cmd_combo_box)
        combo_nose_success = ComboNoseSuccess(self.table_disc)
        if disc.disc_type == 3:
            combo_nose_success.clear()
            combo_nose_success.addItems(["Closed - Left, Wide - Right", "Closed - Right, Wide - Left"])
        combo_nose_success.setCurrentIndex(disc.nose_success)
        txt_time = NumberLineEdit(self.table_disc)
        txt_time.setText(str(disc.time_seconds))
        # txt_time.textChanged[str].connect(self.calculate_total_time())
        self.table_disc.setCellWidget(row_count, 0, combo_disc_type)
        self.table_disc.setCellWidget(row_count, 1, combo_nose_success)
        self.table_disc.setCellWidget(row_count, 2, txt_time)
        self.table_disc.cellWidget(row_count, 2).textChanged[str].connect(self.calculate_total_time)

    def calculate_total_time(self):
        total_time = 0
        for row in range(self.table_disc.rowCount()):
            if self.table_disc.cellWidget(row, 2).text():
                total_time += int(self.table_disc.cellWidget(row, 2).text())
        self.txt_total_time.setText(str(total_time))

    def cb_cmd_combo_box(self, index: int):
        row = self.table_disc.currentRow()
        print("index = " + str(index) + ", row = " + str(row))
        if index == 3:
            self.table_disc.cellWidget(row, 1).clear()
            self.table_disc.cellWidget(row, 1).addItems(["Closed - Left, Wide - Right", "Closed - Right, Wide - Left"])
        else:
            self.table_disc.cellWidget(row, 1).clear()
            self.table_disc.cellWidget(row, 1).addItems(["Left", "Right"])


class ComboDiscType(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        # self.setStyleSheet("fons-size: 25px")
        # self.addItems(['Closed', 'Wide', 'Open', 'Random'])
        self.addItems(['Closed', 'Wide', 'Open', 'Random'])


class ComboNoseSuccess(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        # self.setStyleSheet("fons-size: 25px")
        # self.addItems(['Left', 'Right', 'Standard', 'Both'])
        self.addItems(['Left', 'Right'])


class NumberLineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setValidator(QIntValidator())
