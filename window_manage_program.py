from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi

from Database import Database
from window_new_program import UiNewProgramDialog


class UiManageProgramDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiManageProgramDialog, self).__init__()
        loadUi("window_manage_program.ui", self)
        self.setWindowTitle("Manage Training Programs")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Populate the table
        # self.table_manage = QTableWidget()
        self.table_manage.setColumnCount(5)
        self.table_manage.setHorizontalHeaderLabels(["id", "Name", "Max. Rewards", "Reward Time (ms)",
                                                     "Total Time (s)"])
        self.table_manage.setColumnWidth(0, 50)
        self.table_manage.setColumnWidth(1, 300)
        self.table_manage.setColumnWidth(2, 100)
        self.table_manage.setColumnWidth(3, 120)
        self.table_manage.setColumnWidth(4, 200)
        header = self.table_manage.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.database = Database()
        self.new_program = None
        self.list_program = []
        self.populate_table()

        # Set Button Icon
        self.bt_add.setIcon(QIcon("images/add.png"))
        self.bt_delete.setIcon(QIcon("images/remove.png"))
        self.bt_edit.setIcon(QIcon("images/edit.png"))

        # Connect all buttons to functions
        self.bt_add.clicked.connect(self.bt_cmd_add)
        self.bt_delete.clicked.connect(self.bt_cmd_delete)
        self.bt_edit.clicked.connect(self.bt_cmd_edit)

    def closeEvent(self, event):
        self.closed.emit()

    def populate_table(self):
        self.clear_table()
        self.list_program = self.database.list_program()  # Get list from database
        # Populate the table
        self.table_manage.setRowCount(len(self.list_program))
        row = 0
        for program in self.list_program:
            self.table_manage.setItem(row, 0, QTableWidgetItem(str(program.program_id)))
            self.table_manage.setItem(row, 1, QTableWidgetItem(program.name))
            self.table_manage.setItem(row, 2, QTableWidgetItem(str(program.max_rewards)))
            self.table_manage.setItem(row, 3, QTableWidgetItem(str(program.reward_ms)))
            self.table_manage.setItem(row, 4, QTableWidgetItem(str(program.total_time)))
            row = row + 1

    def clear_table(self):
        while self.table_manage.rowCount() > 0:
            self.table_manage.removeRow(0)

    def bt_cmd_add(self):
        # Create a new window
        self.new_program = UiNewProgramDialog()
        self.new_program.closed.connect(self.populate_table)
        self.new_program.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_program.show()

    def bt_cmd_delete(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            if self.database.check_delete_program(self.list_program[row_id].program_id):
                ret = QMessageBox.question(self, "Delete Training Program", "Are you sure you want to delete " +
                                           self.list_program[row_id].name + "?",
                                           QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    try:
                        self.database.delete_program(self.list_program[row_id].program_id)
                        QMessageBox.information(self, "Success", "Training Program was deleted")
                        self.populate_table()
                    except:
                        QMessageBox.critical(self, "Error", "Error connecting to database")
            else:
                QMessageBox.warning(self, "Warning", "Training Program can't be deleted because\nthere are"
                                                     " experiments using this training program.")
        else:
            QMessageBox.warning(self, "Warning", "Select a Row")

    def bt_cmd_edit(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            if self.database.check_delete_program(self.list_program[row_id].program_id):
                try:
                    self.new_program = UiNewProgramDialog()
                    self.new_program.closed.connect(self.populate_table)
                    self.new_program.edit_program(self.list_program[row_id])
                    self.new_program.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                                   | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
                    self.new_program.show()
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")
            else:
                QMessageBox.warning(self, "Warning", "Training Program can't be edited because\nthere are"
                                                     " experiments using this training program.")

        else:
            QMessageBox.warning(self, "Warning", "Select a Row")
