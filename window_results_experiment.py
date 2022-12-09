from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi

from Database import Database
from window_visualize_result import UiVisualizeResultDialog


class UiResultsExperimentDialog(QDialog):
    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiResultsExperimentDialog, self).__init__()
        loadUi("window_results_experiment.ui", self)
        self.setWindowTitle("Experiment Results")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Populate the table
        # self.table_manage = QTableWidget()
        self.table_manage.setColumnCount(6)
        self.table_manage.setHorizontalHeaderLabels(["id", "Animal", "Training Program", "Experiment Start",
                                                     "Experiment End", "Total Success (%)"])
        self.table_manage.setColumnWidth(0, 50)
        self.table_manage.setColumnWidth(1, 100)
        self.table_manage.setColumnWidth(2, 150)
        self.table_manage.setColumnWidth(3, 150)
        self.table_manage.setColumnWidth(4, 150)
        self.table_manage.setColumnWidth(5, 120)
        header = self.table_manage.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.database = Database()
        self.list_experiment = []
        self.visualize_result = None
        self.populate_table()

        # Set Button Icon
        self.bt_delete.setIcon(QIcon("images/remove.png"))
        self.bt_visualize.setIcon(QIcon("images/eye.png"))

        # Connect buttons to functions
        self.bt_delete.clicked.connect(self.bt_cmd_delete)
        self.bt_visualize.clicked.connect(self.bt_cmd_visualize)

    def bt_cmd_visualize(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            self.visualize_result = UiVisualizeResultDialog(self.list_experiment[row_id])
            self.visualize_result.closed.connect(self.populate_table)
            self.visualize_result.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                           | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            self.visualize_result.show()
        else:
            QMessageBox.warning(self, "Warning", "Select a Row")

    def bt_cmd_delete(self):
        row_id = self.table_manage.currentIndex().row()
        if row_id >= 0:
            ret = QMessageBox.question(self, "Delete Training Experiment", "Are you sure you want to delete"
                                                                           " the experiment?",
                                       QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                try:
                    self.database.delete_experiment(self.list_experiment[row_id].experiment_id)
                    QMessageBox.information(self, "Success", "Experiment was deleted")
                    self.populate_table()
                except:
                    QMessageBox.critical(self, "Error", "Error connecting to database")
        else:
            QMessageBox.warning(self, "Warning", "Select a Row")

    def populate_table(self):
        self.clear_table()
        self.list_experiment = self.database.list_experiment()
        self.table_manage.setRowCount(len(self.list_experiment))
        row = 0
        for experiment in self.list_experiment:
            self.table_manage.setItem(row, 0, QTableWidgetItem(str(experiment.experiment_id)))
            self.table_manage.setItem(row, 1, QTableWidgetItem(experiment.animal.name))
            self.table_manage.setItem(row, 2, QTableWidgetItem(experiment.program.name))
            self.table_manage.setItem(row, 3, QTableWidgetItem(experiment.time_start.strftime("%Y-%m-%d %H:%M:%S")))
            self.table_manage.setItem(row, 4, QTableWidgetItem(experiment.time_end.strftime("%Y-%m-%d %H:%M:%S")))
            success_percentage = 100 * (experiment.right_success + experiment.left_success) \
                                 / (experiment.right_total + experiment.left_total)
            self.table_manage.setItem(row, 5, QTableWidgetItem(str(success_percentage) + " %"))
            row = row + 1

    def clear_table(self):
        while self.table_manage.rowCount() > 0:
            self.table_manage.removeRow(0)
