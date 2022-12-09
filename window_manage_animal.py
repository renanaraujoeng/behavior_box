from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi

from Database import Database
from window_new_animal import UiNewAnimalDialog


class UiManageAnimalDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiManageAnimalDialog, self).__init__()
        loadUi("window_manage_animal.ui", self)
        self.setWindowTitle("Manage Animals")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Populate the table
        # self.table_manage = QTableWidget()
        self.table_manage.setColumnCount(4)
        self.table_manage.setHorizontalHeaderLabels(["id", "Name", "Weight (g)", "Birth Date"])
        self.table_manage.setColumnWidth(0, 50)
        self.table_manage.setColumnWidth(1, 300)
        self.table_manage.setColumnWidth(2, 100)
        self.table_manage.setColumnWidth(3, 300)
        header = self.table_manage.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.database = Database()
        self.new_animal = None
        self.list_animal = []
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
        self.list_animal = self.database.list_animal()
        self.table_manage.setRowCount(len(self.list_animal))
        row = 0
        for animal in self.list_animal:
            self.table_manage.setItem(row, 0, QTableWidgetItem(str(animal.animal_id)))
            self.table_manage.setItem(row, 1, QTableWidgetItem(animal.name))
            self.table_manage.setItem(row, 2, QTableWidgetItem(str(animal.weight)))
            self.table_manage.setItem(row, 3, QTableWidgetItem(animal.birth.strftime("%Y-%m-%d %H:%M:%S")))
            row = row + 1

    def clear_table(self):
        while self.table_manage.rowCount() > 0:
            self.table_manage.removeRow(0)

    def bt_cmd_add(self):
        self.new_animal = UiNewAnimalDialog()
        self.new_animal.closed.connect(self.populate_table)
        self.new_animal.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_animal.show()

    def bt_cmd_delete(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            if self.database.check_delete_animal(self.list_animal[row_id].animal_id):
                ret = QMessageBox.question(self, "Delete Animal", "Are you sure you want to delete " +
                                           self.list_animal[row_id].name + "?",
                                           QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    try:
                        self.database.delete_animal(self.list_animal[row_id].animal_id)
                        QMessageBox.information(self, "Success", "Animal was deleted")
                        self.populate_table()
                    except:
                        QMessageBox.critical(self, "Error", "Error connecting to database")
            else:
                QMessageBox.warning(self, "Warning", "Animal can't be deleted because there are"
                                                     " experiments of this animal")
        else:
            QMessageBox.warning(self, "Warning", "Select a Row")

    def bt_cmd_edit(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            self.new_animal = UiNewAnimalDialog()
            self.new_animal.closed.connect(self.populate_table)
            self.new_animal.edit_animal(self.list_animal[row_id])
            self.new_animal.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                           | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            self.new_animal.show()
        else:
            QMessageBox.warning(self, "Warning", "Select a Row")
