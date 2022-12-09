import datetime
import time
from random import randint

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QTableWidgetItem, QWidget, QHBoxLayout, QMessageBox
from PyQt5.uic import loadUi
from serial import SerialException

from ArduinoSerial import ArduinoSerial
from Database import Database
from CameraVideo import CameraVideo
from ProjectObjects import Discrimination, TrainingExperiment, Resource, Log
from RepeatTimer import RepeatTimer
from window_about import UiAboutDialog
from window_arduino import UiArduinoDialog
from window_manage_animal import UiManageAnimalDialog
from window_manage_program import UiManageProgramDialog
from window_new_animal import UiNewAnimalDialog
from window_new_program import UiNewProgramDialog
from window_results_experiment import UiResultsExperimentDialog


class UiMainWindow(QMainWindow):

    def __init__(self):
        super(UiMainWindow, self).__init__()
        loadUi("window_main.ui", self)
        self.setWindowTitle("Behavior Box")
        self.setWindowIcon(QIcon("images/icon.png"))

        # Set Button icons, Label images, and texts
        self.bt_update.setIcon(QIcon("images/update.png"))
        self.bt_update_cameras.setIcon(QIcon("images/update.png"))
        self.bt_connect.setIcon(QIcon("images/link-on.png"))
        self.bt_add_animal.setIcon(QIcon("images/add.png"))
        self.bt_add_program.setIcon(QIcon("images/add.png"))
        self.bt_play.setIcon(QIcon("images/play-black.png"))
        self.bt_pause.setIcon(QIcon("images/pause-black.png"))
        self.bt_stop.setIcon(QIcon("images/stop-black.png"))
        self.lb_sensor_disc.setPixmap(QPixmap("images/light-gray.png"))
        self.lb_sensor_door.setPixmap(QPixmap("images/light-gray.png"))
        self.lb_sensor_right.setPixmap(QPixmap("images/light-gray.png"))
        self.lb_sensor_left.setPixmap(QPixmap("images/light-gray.png"))
        self.lb_connect_image.setPixmap(QPixmap("images/light-red.png"))
        self.lb_connect_image.setScaledContents(True)
        self.lb_connect_txt.setText("Disconnected")
        # self.status_bar = QStatusBar()
        self.status_bar.showMessage("Waiting for Experiment to Start...")
        self.check_door.setChecked(True)

        # Set menu, buttons and combobox commands
        self.menu_quit.triggered.connect(self.menu_cmd_quit)
        self.menu_animal.triggered.connect(self.menu_cmd_animal)
        self.menu_program.triggered.connect(self.menu_cmd_program)
        self.menu_experiment.triggered.connect(self.menu_cmd_experiment)
        self.menu_about.triggered.connect(self.menu_cmd_about)
        # self.menu_control_box.triggered.connect(self.menu_cmd_control_box)

        self.bt_update.clicked.connect(self.bt_cmd_update)
        self.bt_update_cameras.clicked.connect(self.bt_cmd_update_cameras)
        self.bt_connect.clicked.connect(self.bt_cmd_connect)
        self.bt_add_animal.clicked.connect(self.bt_cmd_add_animal)
        self.bt_add_program.clicked.connect(self.bt_cmd_add_program)
        self.bt_play.clicked.connect(self.bt_cmd_play)
        # self.bt_pause.clicked.connect(self.bt_cmd_pause)
        self.bt_stop.clicked.connect(self.bt_cmd_stop)

        self.cb_camera0.activated[int].connect(self.cb_cmd_camera0)
        self.cb_camera1.activated[int].connect(self.cb_cmd_camera1)
        self.cb_program.activated[int].connect(self.cb_cmd_program)

        # Disable buttons
        self.bt_play.setEnabled(False)
        self.bt_pause.setEnabled(False)
        self.bt_stop.setEnabled(False)

        # Connection to Database, Cameras and Arduino
        self.database = Database()
        self.arduino_serial = ArduinoSerial()
        self.baud_rate = 9600
        self.camera_video0 = CameraVideo()
        self.camera_video1 = CameraVideo()

        # Auxiliary Variables
        self.new_window = None
        self.program = None
        self.list_animal = []
        self.list_program = []
        self.list_com_ports = []
        self.list_disc = []
        self.list_resource = []
        self.list_log = []
        self.disc_type = ['Closed', 'Wide', 'Open', 'Random']
        self.nose_success = ['Left', 'Right']
        self.nose_success_random = ["Closed - Left, Wide - Right", "Closed - Right, Wide - Left"]
        self.success_counter = [0, 0, 0, 0]  # 0 - Left Success, 1 - Left Attempts, 2 - Right Success, 3 - Right Attempt
        self.sensor_status = [2, 2, 2, 2]  # 0 - Discrimination, 1 - Door, 2 - Left, 3 - Right
        self.experiment_status = 0  # 0 - Not Running, 1 - Running, 2 - Paused
        self.is_arduino_connected = 0
        self.is_control_box_open = 0
        self.current_disc = 0
        self.reward_count = 0
        self.time_disc_passed = 0
        self.time_start = None

        # Initiate Program Discrimination Table
        self.table_disc.setColumnCount(4)
        self.table_disc.setHorizontalHeaderLabels(["Discrimination Type", "Nose Success", "Time (s)", "Status"])
        self.table_disc.setColumnWidth(0, 150)
        self.table_disc.setColumnWidth(1, 150)
        self.table_disc.setColumnWidth(2, 100)
        self.table_disc.setColumnWidth(3, 50)
        header = self.table_disc.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        # Populate all combo boxes
        self.populate_cb_animal()
        self.populate_cb_program()
        self.bt_cmd_update()
        self.cb_camera0.clear()
        self.cb_camera1.clear()
        self.cb_camera0.addItem("Select Camera")
        self.cb_camera1.addItem("Select Camera")
        list_cameras = self.camera_video0.return_camera_indexes()
        for camera in list_cameras:
            self.cb_camera0.addItem("Camera " + str(camera))
            self.cb_camera1.addItem("Camera " + str(camera))

        # Create Threads (Function will be called every x seconds)
        self.thread_act_time = 0.1
        self.thread_read_sensors = RepeatTimer(self.thread_act_time, self.thread_function_read_sensors)
        self.thread_close_door = ThreadCloseDoor(0, self)
        self.thread_experiment = ThreadExperiment(0, self)
        self.thread_discrimination = ThreadDiscrimination(Discrimination(0, 0, 0, 0), self)

    def closeEvent(self, event):
        # Terminate all Threads, Serial, Camera and Database connections
        ok_to_quit = True
        if self.experiment_status != 0:
            ret = QMessageBox.question(self, "Experiment in progress", "Are you sure you want to quit? "
                                                                       "All experiment progress will be lost",
                                       QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                ok_to_quit = True
            else:
                ok_to_quit = False
                event.ignore()

        if ok_to_quit:
            self.thread_read_sensors.cancel()
            self.thread_experiment.stop()
            self.thread_discrimination.stop()
            self.thread_close_door.stop()
            self.database.db.close()
            if self.camera_video0.is_created & self.camera_video0.is_running:
                self.camera_video0.stop_capture()
            if self.camera_video1.is_created & self.camera_video1.is_running:
                self.camera_video1.stop_capture()
            if self.arduino_serial.is_connected():
                self.arduino_serial.disconnect()
            event.accept()

    def menu_cmd_quit(self):
        self.close()

    def menu_cmd_experiment(self):
        self.new_window = UiResultsExperimentDialog()
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def menu_cmd_animal(self):
        self.new_window = UiManageAnimalDialog()
        self.new_window.closed.connect(self.populate_cb_animal)
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def menu_cmd_program(self):
        self.new_window = UiManageProgramDialog()
        self.new_window.closed.connect(self.populate_cb_program)
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def menu_cmd_about(self):
        self.new_window = UiAboutDialog()
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def menu_cmd_control_box(self):
        if self.arduino_serial.is_connected():
            self.new_window = UiArduinoDialog()
            self.new_window.arduino_serial = self.arduino_serial
            self.new_window.bt_cmd_connect()
            self.new_window.closed.connect(self.control_box_close)
            self.is_control_box_open = 1
            # Limit the control if the experiment is running
            if self.experiment_status == 0:
                self.new_window.enable_com(True)
            else:
                self.new_window.enable_com(False)
            self.new_window.show()
        else:
            QMessageBox.warning(self, "Warning", "Connect Arduino before accessing the Behavior Box Control")

    def control_box_close(self):
        self.is_control_box_open = 0
        print("Control Closed")

    def bt_cmd_update(self):
        self.cb_com_ports.clear()
        self.cb_com_ports.addItem("Select Arduino")
        self.list_com_ports = self.arduino_serial.list_arduino_com_ports()
        for com_port in self.list_com_ports:
            self.cb_com_ports.addItem(com_port.description)

    def bt_cmd_update_cameras(self):
        self.cb_camera0.clear()
        self.cb_camera1.clear()
        self.cb_camera0.addItem("Select Camera")
        self.cb_camera1.addItem("Select Camera")
        if self.camera_video0.is_running:
            self.camera_video0.stop_capture()
        if self.camera_video1.is_running:
            self.camera_video1.stop_capture()
        list_cameras = self.camera_video0.return_camera_indexes()
        for camera in list_cameras:
            self.cb_camera0.addItem("Camera " + str(camera))
            self.cb_camera1.addItem("Camera " + str(camera))
        self.lb_camera0.clear()
        self.lb_camera1.clear()

    def bt_cmd_connect(self):
        if self.is_arduino_connected:
            self.thread_read_sensors.cancel()
            self.arduino_serial.disconnect()
            self.bt_connect.setText("Connect")
            self.bt_connect.setIcon(QIcon("images/link-on.png"))
            self.cb_com_ports.setEnabled(True)
            self.bt_update.setEnabled(True)
            self.bt_play.setEnabled(False)
            self.lb_connect_txt.setText("Disconnected")
            self.lb_connect_image.setPixmap(QPixmap("images/light-red.png"))
            self.lb_sensor_disc.setPixmap(QPixmap("images/light-gray.png"))
            self.lb_sensor_door.setPixmap(QPixmap("images/light-gray.png"))
            self.lb_sensor_right.setPixmap(QPixmap("images/light-gray.png"))
            self.lb_sensor_left.setPixmap(QPixmap("images/light-gray.png"))
            self.is_arduino_connected = 0
            self.sensor_status = [2, 2, 2, 2]
        else:
            # self.cb_com_ports = QComboBox()
            if self.cb_com_ports.currentIndex() > 0:
                try:
                    self.arduino_serial = ArduinoSerial(self.list_com_ports[self.cb_com_ports.currentIndex() - 1]
                                                        .device, self.baud_rate)
                except ValueError:
                    QMessageBox.critical(self, "Error", str(ValueError))

                if self.arduino_serial.is_connected():
                    # Set button to disconnect
                    self.bt_connect.setText("Disconnect")
                    self.bt_connect.setIcon(QIcon("images/link-off.png"))
                    self.cb_com_ports.setEnabled(False)
                    self.bt_update.setEnabled(False)
                    self.bt_play.setEnabled(True)
                    self.lb_connect_txt.setText("Connected")
                    self.lb_connect_image.setPixmap(QPixmap("images/light-green.png"))
                    self.is_arduino_connected = 1
                    # Start Reading Thread to receive sensor information
                    self.thread_read_sensors.cancel()
                    self.thread_read_sensors = RepeatTimer(self.thread_act_time, self.thread_function_read_sensors)
                    self.thread_read_sensors.start()
            else:
                QMessageBox.warning(self, "Warning", "Select Arduino to connect")

    def bt_cmd_add_animal(self):
        self.new_window = UiNewAnimalDialog()
        self.new_window.closed.connect(self.populate_cb_animal)
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def bt_cmd_add_program(self):
        # Create a new window
        self.new_window = UiNewProgramDialog()
        self.new_window.closed.connect(self.populate_cb_program)
        self.new_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint
                                       | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.new_window.show()

    def bt_cmd_play(self):
        if self.test_fields_experiment_start():
            if self.experiment_status == 0:
                print("Experiment Start")
                self.experiment_status = 1
                self.bt_play.setEnabled(False)
                self.bt_pause.setEnabled(True)
                self.bt_stop.setEnabled(True)
                self.lb_status.setText("Running")
                self.time_start = datetime.datetime.now()
                self.txt_start.setText(self.time_start.strftime("%Y-%m-%d %H:%M:%S"))
                self.current_disc = 0
                self.time_disc_passed = 0
                self.reward_count = 0
                self.success_counter = [0, 0, 0, 0]
                self.list_resource = []
                self.list_log = []
                self.txt_left.setText("0 / 0")
                self.txt_right.setText("0 / 0")
                self.txt_total.setText("0 / 0")

                # Update image to table
                widget_image = QWidget()
                label_image = QLabelImage(self.table_disc)
                label_image.set_image("images/play-circle.png")
                layout_image = QHBoxLayout(widget_image)
                layout_image.addWidget(label_image)
                layout_image.setAlignment(Qt.AlignCenter)
                layout_image.setContentsMargins(0, 0, 0, 0)
                self.table_disc.setCellWidget(0, 3, widget_image)
                # Stop Reading sensor Thread
                # self.thread_read_sensors.cancel()

                # Start first Discrimination Protocol
                # self.thread_discrimination = ThreadDiscrimination(self.arduino_serial, self.list_disc[0],
                #                                                   self.program.reward_ms, self)
                self.thread_discrimination = ThreadDiscrimination(self.list_disc[0], self)
                self.thread_discrimination.incoming_serial_read.connect(self.incoming_sensor_read)
                self.thread_discrimination.finished_success.connect(self.finished_discrimination)
                self.thread_discrimination.start()

                # Start Experiment Thread
                self.thread_experiment = ThreadExperiment(self.program.total_time, self)
                self.thread_experiment.second_counter.connect(self.thread_function_experiment)
                self.thread_experiment.finished.connect(self.thread_discrimination.stop)
                self.thread_experiment.finished.connect(self.finished_experiment)
                self.thread_experiment.start()
                self.enable_experiment_running(False)

                # Start Video write to mp4
                if self.cb_camera0.currentIndex() > 0:
                    date = self.time_start
                    file_name = "videos/Capture%d_%s-%s-%s_%s-%s-%s.mp4" % (0, date.year, date.month, date.day,
                                                                            date.hour, date.minute, date.second)
                    self.list_resource.append(Resource(0, 0, file_name))
                    self.camera_video0.begin_saving_video(file_name)
                if self.cb_camera1.currentIndex() > 0:
                    date = self.time_start
                    file_name = "videos/Capture%d_%s-%s-%s_%s-%s-%s.mp4" % (1, date.year, date.month, date.day,
                                                                            date.hour, date.minute, date.second)
                    self.list_resource.append(Resource(0, 0, file_name))
                    self.camera_video1.begin_saving_video(file_name)

            elif self.experiment_status == 2:
                print("Experiment Resume")
                self.experiment_status = 1
                self.bt_play.setEnabled(False)
                self.bt_pause.setEnabled(True)
                self.bt_stop.setEnabled(True)
                self.lb_status.setText("Running")
                # Resume Experiment Thread
                self.thread_experiment.resume()

    def test_fields_experiment_start(self):
        if (self.cb_camera0.currentIndex() == 0) & (self.cb_camera1.currentIndex() == 0):
            QMessageBox.warning(self, "Warning", "Choose at least one camera")
            return False
        if self.cb_animal.currentIndex() == 0:
            QMessageBox.warning(self, "Warning", "Choose the Animal for the experiment")
            return False
        if self.cb_program.currentIndex() == 0:
            QMessageBox.warning(self, "Warning", "Choose the Training Program for the experiment")
            return False
        return True

    def bt_cmd_pause(self):
        print("Experiment Pause")
        self.experiment_status = 2
        self.bt_play.setEnabled(True)
        self.bt_pause.setEnabled(False)
        self.bt_stop.setEnabled(True)
        self.lb_status.setText("Paused")
        # Pause Threads
        self.thread_experiment.pause()

    def bt_cmd_stop(self):
        if (self.experiment_status == 1) | (self.experiment_status == 2):
            ret = QMessageBox.question(self, "Experiment in progress", "Are you sure you want to stop? "
                                                                       "All experiment progress will be lost",
                                       QMessageBox.Yes | QMessageBox.No)
        else:
            ret = QMessageBox.Yes
        if ret == QMessageBox.Yes:
            print("Experiment STOP")

            # Stop Recording camera
            if (self.experiment_status == 1) | (self.experiment_status == 3):
                # End Threads
                self.thread_experiment.stop()
                self.thread_discrimination.stop()
                if self.cb_camera0.currentIndex() > 0:
                    self.camera_video0.stop_saving_video()
                if self.cb_camera1.currentIndex() > 0:
                    self.camera_video1.stop_saving_video()

            # time.sleep(2)

            # Clear all Information
            self.experiment_status = 0
            self.bt_play.setEnabled(True)
            self.bt_pause.setEnabled(False)
            self.bt_stop.setEnabled(False)
            self.lb_status.setText("Not Running")
            self.lb_time_elapsed.setText("00:00:00")
            self.txt_start.setText("")
            self.txt_left.setText("")
            self.txt_right.setText("")
            self.txt_total.setText("")
            self.status_bar.showMessage("Waiting for Experiment to start...")
            self.progress_bar.setValue(0)
            self.enable_experiment_running(True)
            self.cb_cmd_program()

    def cb_cmd_program(self):
        self.clear_table_disc()
        if self.cb_program.currentIndex() > 0:
            program_id = self.list_program[self.cb_program.currentIndex() - 1].program_id
            self.program = self.database.search_program_id(program_id)
            self.list_disc = self.database.list_disc(program_id)
            row = 0
            for disc in self.list_disc:
                self.table_disc.setRowCount(row + 1)
                item = QTableWidgetItem(self.disc_type[disc.disc_type])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_disc.setItem(row, 0, item)
                if disc.disc_type == 3:
                    item = QTableWidgetItem(self.nose_success_random[disc.nose_success])
                else:
                    item = QTableWidgetItem(self.nose_success[disc.nose_success])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_disc.setItem(row, 1, item)
                item = QTableWidgetItem(str(disc.time_seconds))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_disc.setItem(row, 2, item)
                widget_image = QWidget()
                label_image = QLabelImage(self.table_disc)
                label_image.set_image("images/wait-circle.png")
                layout_image = QHBoxLayout(widget_image)
                layout_image.addWidget(label_image)
                layout_image.setAlignment(Qt.AlignCenter)
                layout_image.setContentsMargins(0, 0, 0, 0)
                self.table_disc.setCellWidget(row, 3, widget_image)
                row += 1

    def cb_cmd_camera0(self):
        if self.cb_camera0.currentIndex() > 0:
            camera_index = int(self.cb_camera0.currentText().replace("Camera ", ""))
            print(camera_index)
            if self.camera_video1.is_running & (camera_index == self.camera_video1.camera_index):
                self.cb_camera0.setCurrentIndex(0)
                QMessageBox.warning(self, "Warning", "Camera already running")
            else:
                if self.camera_video0.is_created & self.camera_video0.is_running:
                    self.camera_video0.stop_capture()
                self.camera_video0 = CameraVideo(self, camera_index, self.lb_camera0)
                self.camera_video0.begin_capture()
        else:
            if self.camera_video0.is_created & self.camera_video0.is_running:
                self.camera_video0.stop_capture()
            self.lb_camera0.clear()

    def cb_cmd_camera1(self):
        if self.cb_camera1.currentIndex() > 0:
            camera_index = int(self.cb_camera1.currentText().replace("Camera ", ""))
            print(camera_index)
            if self.camera_video0.is_running & (camera_index == self.camera_video0.camera_index):
                self.cb_camera1.setCurrentIndex(0)
                QMessageBox.warning(self, "Warning", "Camera already running")
            else:
                if self.camera_video1.is_created & self.camera_video1.is_running:
                    self.camera_video1.stop_capture()
                self.camera_video1 = CameraVideo(self, camera_index, self.lb_camera1)
                self.camera_video1.begin_capture()
        else:
            if self.camera_video1.is_created & self.camera_video1.is_running:
                self.camera_video1.stop_capture()
            self.lb_camera1.clear()

    def clear_table_disc(self):
        while self.table_disc.rowCount() > 0:
            self.table_disc.removeRow(0)

    def populate_cb_animal(self):
        # self.cb_animal = QComboBox()
        if self.experiment_status == 0:
            self.cb_animal.clear()
            self.list_animal = self.database.list_animal_names()
            self.cb_animal.addItem("Select Animal")
            for animal in self.list_animal:
                self.cb_animal.addItem(str(animal.animal_id) + " : " + animal.name)

    def populate_cb_program(self):
        # self.cb_program = QComboBox()
        if self.experiment_status == 0:
            self.cb_program.clear()
            self.clear_table_disc()
            self.list_program = self.database.list_program_names()
            self.cb_program.addItem("Select Training Program")
            for program in self.list_program:
                time_txt = time.strftime("%H:%M:%S", time.gmtime(program.total_time))
                self.cb_program.addItem(str(program.program_id) + " : " + program.name + " (" + time_txt + ")")

    def thread_function_read_sensors(self):
        # print("Reading sensor")
        if self.arduino_serial.is_connected():
            try:
                if self.arduino_serial.in_waiting():
                    txt = self.arduino_serial.read()
                    print("Reading: " + txt)
                    self.incoming_sensor_read(txt)
                    if self.is_control_box_open:
                        self.new_window.connect_read_sensors(txt)
            except SerialException:
                print(SerialException)
                self.thread_read_sensors.cancel()
                if self.is_control_box_open:
                    self.new_window.close()
                self.experiment_status = 3
                self.bt_cmd_stop()
                self.bt_cmd_connect()
                self.bt_cmd_update()
                # QMessageBox.critical(self, "Error", "Arduino was disconnected")

    def incoming_sensor_read(self, txt: str):
        if txt == "p0=0":
            self.lb_sensor_disc.setPixmap(QPixmap("images/light-red.png"))
            self.sensor_status[0] = 0
        elif txt == "p0=1":
            self.lb_sensor_disc.setPixmap(QPixmap("images/light-green.png"))
            self.sensor_status[0] = 1
        elif txt == "p1=0":
            self.lb_sensor_door.setPixmap(QPixmap("images/light-red.png"))
            self.sensor_status[1] = 0
        elif txt == "p1=1":
            self.lb_sensor_door.setPixmap(QPixmap("images/light-green.png"))
            self.sensor_status[1] = 1
        elif txt == "p2=0":
            self.lb_sensor_left.setPixmap(QPixmap("images/light-red.png"))
            self.sensor_status[2] = 0
        elif txt == "p2=1":
            self.lb_sensor_left.setPixmap(QPixmap("images/light-green.png"))
            self.sensor_status[2] = 1
        elif txt == "p3=0":
            self.lb_sensor_right.setPixmap(QPixmap("images/light-red.png"))
            self.sensor_status[3] = 0
        elif txt == "p3=1":
            self.lb_sensor_right.setPixmap(QPixmap("images/light-green.png"))
            self.sensor_status[3] = 1

    # This thread will update all values every 1s
    def thread_function_experiment(self, seconds):
        if self.experiment_status == 1:
            # Update time label and experiment progress bar
            time_txt = time.strftime("%H:%M:%S", time.gmtime(seconds))
            self.lb_time_elapsed.setText(time_txt)
            experiment_percentage = int(100*(seconds/self.program.total_time))
            self.progress_bar.setValue(experiment_percentage)
            # Go through all the Discrimination protocols
            if self.current_disc < len(self.list_disc):
                if (seconds - self.time_disc_passed) >= self.list_disc[self.current_disc].time_seconds:
                    # Update table images
                    widget_image = QWidget()
                    label_image = QLabelImage(self.table_disc)
                    label_image.set_image("images/check-circle.png")
                    layout_image = QHBoxLayout(widget_image)
                    layout_image.addWidget(label_image)
                    layout_image.setAlignment(Qt.AlignCenter)
                    layout_image.setContentsMargins(0, 0, 0, 0)
                    self.table_disc.setCellWidget(self.current_disc, 3, widget_image)

                    self.time_disc_passed += self.list_disc[self.current_disc].time_seconds
                    self.current_disc += 1

                    if self.current_disc < len(self.list_disc):
                        # Start Discrimination Thread
                        if self.thread_discrimination.is_running:
                            self.thread_discrimination.stop()
                        self.thread_discrimination = ThreadDiscrimination(self.list_disc[self.current_disc], self)
                        self.thread_discrimination.finished_success.connect(self.finished_discrimination)
                        self.thread_discrimination.incoming_serial_read.connect(self.incoming_sensor_read)
                        self.thread_experiment.finished.connect(self.thread_discrimination.stop)
                        self.thread_discrimination.start()
                        # Update table images
                        widget_image = QWidget()
                        label_image = QLabelImage(self.table_disc)
                        label_image.set_image("images/play-circle.png")
                        layout_image = QHBoxLayout(widget_image)
                        layout_image.addWidget(label_image)
                        layout_image.setAlignment(Qt.AlignCenter)
                        layout_image.setContentsMargins(0, 0, 0, 0)
                        self.table_disc.setCellWidget(self.current_disc, 3, widget_image)

    def finished_discrimination(self, success: int):
        if success == 0:
            # Left Success
            self.success_counter[0] += 1
            self.success_counter[1] += 1
            self.txt_left.setText(str(self.success_counter[0]) + " / " + str(self.success_counter[1]))
        elif success == 1:
            # Left Failure
            self.success_counter[1] += 1
            self.txt_left.setText(str(self.success_counter[0]) + " / " + str(self.success_counter[1]))
        elif success == 2:
            # Right Success
            self.success_counter[2] += 1
            self.success_counter[3] += 1
            self.txt_right.setText(str(self.success_counter[2]) + " / " + str(self.success_counter[3]))
        elif success == 3:
            # Right Failure
            self.success_counter[3] += 1
            self.txt_right.setText(str(self.success_counter[2]) + " / " + str(self.success_counter[3]))
        self.txt_total.setText(str(self.success_counter[0] + self.success_counter[2]) + " / " +
                               str(self.success_counter[1] + self.success_counter[3]))
        # self.thread_read_sensors.cancel()
        # self.thread_read_sensors = RepeatTimer(self.thread_act_time, self.thread_function_read_sensors)
        # self.thread_read_sensors.start()

    def finished_experiment(self):
        self.experiment_status = 0

        # End Discrimination Thread
        self.thread_discrimination.stop()
        # Initiate Thread to read sensor
        # self.thread_read_sensors.cancel()
        # self.thread_read_sensors = RepeatTimer(self.thread_act_time, self.thread_function_read_sensors)
        # self.thread_read_sensors.start()
        print("Experiment Finished")

        # Stop Recording camera
        if self.cb_camera0.currentIndex() > 0:
            self.camera_video0.stop_saving_video()
        if self.cb_camera1.currentIndex() > 0:
            self.camera_video1.stop_saving_video()

        time_end = datetime.datetime.now()
        self.status_bar.showMessage("Experiment Finished.")
        QMessageBox.information(self, "Experiment Finished",
                                'Experiment is finished, Press "Stop" to start another one')
        # time.sleep(5)
        # Save Experiment data to database
        animal = self.list_animal[self.cb_animal.currentIndex() - 1]
        program = self.program
        # time_end = datetime.datetime.now()
        experiment = TrainingExperiment(0, animal, program, self.time_start, time_end, self.success_counter[0],
                                        self.success_counter[1], self.success_counter[2], self.success_counter[3],
                                        self.list_resource, self.list_log)
        self.database.insert_experiment(experiment)
        # QMessageBox.information(self, "Experiment Finished",
        #                         'Experiment is finished, Press "Stop" to start another one')

    def add_resource(self, filename: str):
        self.list_resource.append(Resource(0, 0, filename))

    def enable_experiment_running(self, status: bool):
        self.bt_connect.setEnabled(status)
        self.cb_camera0.setEnabled(status)
        self.cb_camera1.setEnabled(status)
        self.bt_update_cameras.setEnabled(status)
        self.cb_animal.setEnabled(status)
        self.cb_program.setEnabled(status)


class QLabelImage(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText("")
        self.setScaledContents(True)
        self.setFixedSize(22, 22)

    def set_image(self, path: str):
        pixmap = QPixmap(path)
        self.setPixmap(pixmap)


class ThreadExperiment(QThread):

    second_counter = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()

    def __init__(self, total_time: int, parent=None):
        super(ThreadExperiment, self).__init__(parent)
        self.is_running = True
        self.seconds = 0
        self.total_time = total_time

    def run(self):
        print("Starting Experiment")
        while self.is_running:
            # print("Seconds = "+str(self.seconds))
            time.sleep(1)
            self.seconds += 1
            self.second_counter.emit(self.seconds)
            if self.seconds >= self.total_time:
                self.finished.emit()
                self.is_running = False
                break

    def resume(self):
        self.is_running = True
        print("Resume Experiment")

    def pause(self):
        self.is_running = False
        print("Pause Experiment")

    def stop(self):
        self.is_running = False
        print("Stopping Experiment")
        # self.terminate()


class ThreadDiscrimination(QThread):

    # 0 - Left Success, 1 - Left Failure, 2 - Right Success, 3 - Right Failure
    finished_success = QtCore.pyqtSignal(int)
    incoming_serial_read = QtCore.pyqtSignal(str)

    def __init__(self, disc: Discrimination, parent: UiMainWindow):
        super(ThreadDiscrimination, self).__init__(parent)
        self.is_running = False
        self.seconds = 0
        self.arduino_serial = parent.arduino_serial
        self.disc = disc
        if parent.program is None:
            self.reward_ms = 0
        else:
            self.reward_ms = parent.program.reward_ms
            self.max_rewards = parent.program.max_rewards
        self.success = 1
        self.parent = parent
        self.sensor_status = self.parent.sensor_status
        self.thread_door_close = self.parent.thread_close_door
        self.thread_act_time = self.parent.thread_act_time
        self.disc_type_names = self.parent.disc_type
        self.nose_success_names = self.parent.nose_success
        # self.is_control_box_open = control_open

    def run(self):
        self.is_running = True
        self.parent.thread_close_door.stop()
        print("Starting Discrimination")
        # Verify if Discrimination is random
        if self.disc.disc_type == 3:
            disc_type = randint(0, 1)
            if self.disc.nose_success == 0:  # If Closed - Left, Wide - Right
                if disc_type == 0:  # If Discrimination type is Closed
                    nose_success = 0  # Success on Left side
                else:  # if Discrimination type is Wide
                    nose_success = 1  # Success on Right side
            else:  # If Closed - Right, Wide - Left
                if disc_type == 0:  # If Discrimination type is Closed
                    nose_success = 1  # Success on Right side
                else:  # if Discrimination type is Wide
                    nose_success = 0  # Success on Left side
        else:
            disc_type = self.disc.disc_type
            nose_success = self.disc.nose_success
        # Define the success
        reward = nose_success
        if reward == 0:  # If reward is on Left
            self.success = 1  # Define Left Failure
        elif reward == 1:  # If reward is on Right
            self.success = 3  # Define Right Failure
        if self.is_running:
            try:
                # close both rewards
                self.arduino_serial.send("s3=0")
                self.arduino_serial.send("s4=0")
                # Send command to proper Discrimination protocol
                self.arduino_serial.send("disc="+str(disc_type))
                # Send command to open door
                self.arduino_serial.send("s0=1")
            except SerialException:
                print("Problem sending information to arduino")
            # Wait for discrimination sensor
            if self.arduino_serial.is_connected():
                text = self.disc_type_names[disc_type] + " test with " + self.nose_success_names[nose_success] + \
                       " success initiated. Waiting for Discrimination Sensor..."
                self.parent.status_bar.showMessage(text)
                self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                print("Waiting Discrimination Sensor")
                while self.is_running:
                    if self.sensor_status[0] == 0:
                        break
                    time.sleep(self.thread_act_time)
            if self.is_running:
                self.parent.status_bar.showMessage("Sensor Activated. Opening Rewards...")
                self.parent.list_log.append(Log(0, datetime.datetime.now(), "Sensor Activated. Opening Rewards..."))
                # Open both rewards
                try:
                    self.arduino_serial.send("s3=1")
                    self.arduino_serial.send("s4=1")
                except SerialException:
                    print("Problem sending information to arduino")

                #         print("Waiting Door Sensor")
                #         self.parent.status_bar.showMessage("Waiting Door Sensor...")
                #         self.parent.list_log.append(Log(0, datetime.datetime.now(), "Waiting Door Sensor..."))

                # Start Thread to close door with 5 seconds
                self.parent.thread_close_door.stop()
                self.parent.thread_close_door = ThreadCloseDoor(5, self.parent)
                self.parent.thread_close_door.start()

            if self.is_running:
                # Wait for sensor reward
                self.parent.status_bar.showMessage("Waiting Reward Sensor...")
                self.parent.list_log.append(Log(0, datetime.datetime.now(), "Waiting Reward Sensor..."))
                print("Waiting Reward Sensor")
            while self.is_running:
                if self.sensor_status[2] == 0:
                    if reward == 0:
                        if (self.max_rewards == 0) | (self.parent.reward_count <= self.max_rewards):
                            text = "Discrimination Success, Rewarded Left. Waiting next Discrimination..."
                            self.parent.status_bar.showMessage(text)
                            self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                            try:
                                self.arduino_serial.send("p=1=" + str(self.reward_ms))  # Send Reward signal
                            except SerialException:
                                print("Problem sending information to arduino")
                        else:
                            text = "Discrimination Success, No Reward (Reached Max). Waiting next Discrimination..."
                            self.parent.status_bar.showMessage(text)
                            self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                        self.success = 0  # Define Left Success
                        self.parent.reward_count += 1
                    else:
                        text = "Discrimination Failure. Waiting next Discrimination..."
                        self.parent.status_bar.showMessage(text)
                        self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                    break
                #    if incoming == "p3=0":
                if self.sensor_status[3] == 0:
                    if reward == 1:
                        if (self.max_rewards == 0) | (self.parent.reward_count <= self.max_rewards):
                            text = "Discrimination Success, Rewarded Right. Waiting next Discrimination..."
                            self.parent.status_bar.showMessage(text)
                            self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                            try:
                                self.arduino_serial.send("p=2=" + str(self.reward_ms))  # Send Reward signal
                            except SerialException:
                                print("Problem sending information to arduino")
                        else:
                            text = "Discrimination Success, No Reward (Reached Max). Waiting next Discrimination..."
                            self.parent.status_bar.showMessage(text)
                            self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                        self.success = 2  # Define Right Success
                        self.parent.reward_count += 1

                    else:
                        text = "Discrimination Failure. Waiting next Discrimination..."
                        self.parent.status_bar.showMessage(text)
                        self.parent.list_log.append(Log(0, datetime.datetime.now(), text))
                    break
                time.sleep(self.thread_act_time)
            time.sleep(2)
            self.stop()

    def pause(self):
        self.is_running = False

    def stop(self):
        if self.is_running:
            self.is_running = False
            # Set all to initial positions
            try:
                self.arduino_serial.send("disc=2")
                self.arduino_serial.send("s3=0")
                self.arduino_serial.send("s4=0")
            except SerialException:
                print("Problem sending information to arduino")
            # Begin Thread to close door in 5 seconds
            self.parent.thread_close_door.stop()
            self.parent.thread_close_door = ThreadCloseDoor(5, self.parent)
            self.parent.thread_close_door.start()
            print("Stopping Discrimination")
            self.finished_success.emit(self.success)
            # self.terminate()


class ThreadCloseDoor(QThread):

    finished = QtCore.pyqtSignal()

    def __init__(self, time_wait_seconds: float, parent: UiMainWindow):
        super(ThreadCloseDoor, self).__init__(parent)
        self.time_seconds = time_wait_seconds
        self.is_running = False
        self.sensor_status = parent.sensor_status
        self.arduino_serial = parent.arduino_serial
        self.check_box = parent.check_door
        # self.check_box = QCheckBox()
        self.thread_act_time = parent.thread_act_time

    def run(self):
        self.is_running = True
        time.sleep(self.time_seconds)
        if self.check_box.isChecked():
            while self.is_running:
                if self.sensor_status[1] == 1:
                    # Close door
                    try:
                        self.arduino_serial.send("s0=0")
                    except SerialException:
                        print("Problem sending information to arduino")
                    break
                time.sleep(self.thread_act_time)
        else:
            if self.is_running:
                try:
                    self.arduino_serial.send("s0=0")
                except SerialException:
                    print("Problem sending information to arduino")

    def stop(self):
        self.is_running = False
        # self.terminate()
