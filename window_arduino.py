# from PyQt5.QtCore import QThread
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from serial import SerialException

from ArduinoSerial import ArduinoSerial
from RepeatTimer import RepeatTimer


class UiArduinoDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self):
        super(UiArduinoDialog, self).__init__()
        loadUi("window_arduino.ui", self)

        self.setWindowIcon(QIcon("images/icon.png"))
        self.setWindowTitle("Behavior Box Control")
        self.setFixedSize(800, 600)
        # Load All images into labels
        pixmap = QPixmap('images/light-gray.png')
        self.lb_sensor_disc.setPixmap(pixmap)
        self.lb_sensor_disc.setScaledContents(True)

        self.lb_sensor_door.setPixmap(pixmap)
        self.lb_sensor_door.setScaledContents(True)

        self.lb_sensor_reward_left.setPixmap(pixmap)
        self.lb_sensor_reward_left.setScaledContents(True)

        self.lb_sensor_reward_right.setPixmap(pixmap)
        self.lb_sensor_reward_right.setScaledContents(True)

        self.list_sensors = []
        sensor = SerialSensor(self.lb_sensor_disc, self.lb_sensor_disc_count, 0, 2)
        self.list_sensors.append(sensor)
        sensor = SerialSensor(self.lb_sensor_door, self.lb_sensor_door_count, 0, 2)
        self.list_sensors.append(sensor)
        sensor = SerialSensor(self.lb_sensor_reward_left, self.lb_sensor_reward_left_count, 0, 2)
        self.list_sensors.append(sensor)
        sensor = SerialSensor(self.lb_sensor_reward_right, self.lb_sensor_reward_right_count, 0, 2)
        self.list_sensors.append(sensor)

        pixmap = QPixmap('images/disc-wall-open.png')
        self.lb_disc_wall.setPixmap(pixmap)
        self.lb_disc_wall.setScaledContents(True)

        pixmap = QPixmap('images/door-closed.png')
        self.lb_door.setPixmap(pixmap)
        self.lb_door.setScaledContents(True)

        pixmap = QPixmap('images/reward-closed.png')
        self.lb_reward_left.setPixmap(pixmap)
        self.lb_reward_left.setScaledContents(True)

        self.lb_reward_right.setPixmap(pixmap)
        self.lb_reward_right.setScaledContents(True)

        self.txt_reward_right.setValidator(QIntValidator())
        self.txt_reward_left.setValidator(QIntValidator())

        # Connect all buttons and combobox to respective functions
        # self.cb_com_ports.activated[int].connect(self.cb_cmd_com_ports)
        self.cb_disc_wall.activated[int].connect(self.cb_cmd_disc_wall)
        # self.bt_update.clicked.connect(self.bt_cmd_update)
        self.bt_door_open.clicked.connect(self.bt_cmd_door_open)
        self.bt_door_close.clicked.connect(self.bt_cmd_door_close)
        self.bt_reward_left_open.clicked.connect(self.bt_cmd_reward_left_open)
        self.bt_reward_left_close.clicked.connect(self.bt_cmd_reward_left_close)
        self.bt_reward_right_open.clicked.connect(self.bt_cmd_reward_right_open)
        self.bt_reward_right_close.clicked.connect(self.bt_cmd_reward_right_close)
        # self.bt_connect.clicked.connect(self.bt_cmd_connect)
        # self.bt_disconnect.clicked.connect(self.bt_cmd_disconnect)
        self.bt_reward_left.clicked.connect(self.bt_cmd_reward_left)
        self.bt_reward_right.clicked.connect(self.bt_cmd_reward_right)
        # Enable or Disable widgets
        # self.bt_disconnect.setEnabled(False)
        self.enable_com(False)

        # Create Arduino Serial Communication class
        self.arduino_serial = ArduinoSerial()
        self.baud_rate = 9600
        # List all available arduino COM ports on combobox
        # self.com_list = self.arduino_serial.list_arduino_com_ports()
        # self.cb_com_ports = QComboBox()
        # for p in self.com_list:
        #    self.cb_com_ports.addItem(p.description)
        # Create Threads
        # self.thread_read = RepeatTimer(0.1, self.thread_read_sensors)  # Repeat the function every x seconds

    # Event called when the application is closed
    def closeEvent(self, event):
        print("CLOSED APPLICATION")
        # self.thread_read.cancel()  # Finnish the Thread
        # if self.arduino_serial.is_connected():
        #    self.arduino_serial.disconnect()  # Close Arduino connection
        self.closed.emit()

    # -------------COMMANDS: ComboBox and Buttons----------------
    def cb_cmd_com_ports(self, index):
        print("COM PORT = ", self.com_list[index])

    def cb_cmd_disc_wall(self, index):
        print("DISC WALL = ", index)
        try:
            self.arduino_serial.send("disc=" + str(index))
            self.show_disc_wall(index)
        except SerialException:
            print(SerialException)
            # QMessageBox.warning(self, "Error", "Arduino was disconnected")
            self.bt_cmd_disconnect()
            self.bt_cmd_update()

    def bt_cmd_reward_left_open(self):
        print("Open Left Reward")
        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s3=1")
                self.show_reward_left(1)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_reward_left_close(self):
        print("Close Left Reward")
        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s3=0")
                self.show_reward_left(0)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_reward_left(self):
        print("Left Reward")
        if self.arduino_serial.is_connected() & (self.txt_reward_left.text() != ""):
            try:
                self.arduino_serial.send("p=1=" + self.txt_reward_left.text())
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_reward_right_open(self):
        print("Open Right Reward")
        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s4=1")
                self.show_reward_right(1)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_reward_right_close(self):
        print("Close Right Reward")
        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s4=0")
                self.show_reward_right(0)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_reward_right(self):
        print("Right Reward")
        # self.txt_reward_right = QLineEdit()
        if self.arduino_serial.is_connected() & (self.txt_reward_right.text() != ""):
            try:
                self.arduino_serial.send("p=2=" + self.txt_reward_right.text())
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_door_open(self):
        print("Open Door")

        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s0=1")
                self.show_door(1)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_door_close(self):
        print("Close Door")

        if self.arduino_serial.is_connected():
            try:
                self.arduino_serial.send("s0=0")
                self.show_door(0)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

    def bt_cmd_connect(self):
        # Create Connection to Arduino
        if self.arduino_serial.is_connected():
            print("Connect")
            # pixmap = QPixmap('images/right.png')
            # self.lb_connection.setPixmap(pixmap)
            # self.bt_connect.setEnabled(False)
            # self.bt_update.setEnabled(False)
            # self.bt_disconnect.setEnabled(True)
            self.enable_com(True)
            # self.thread_read = RepeatTimer(0.1, self.thread_read_sensors)
            # self.thread_read.start()

    def bt_cmd_disconnect(self):
        self.arduino_serial.disconnect()
        print("Disconnect")
        # pixmap = QPixmap('images/wrong.png')
        # self.lb_connection.setPixmap(pixmap)
        # self.bt_connect.setEnabled(True)
        # self.bt_update.setEnabled(True)
        # self.bt_disconnect.setEnabled(False)
        self.enable_com(False)
        # self.thread_read.cancel()
        self.close()

    def bt_cmd_update(self):
        print("Update")
        # List all available arduino COM ports on combobox
        self.com_list = self.arduino_serial.list_arduino_com_ports()
        self.cb_com_ports.clear()
        for p in self.com_list:
            self.cb_com_ports.addItem(p.description)
        self.cb_com_ports.setFocus()

    # -------------COMMANDS to show stuff on the screen----------------
    def enable_com(self, is_true: bool):
        self.cb_disc_wall.setEnabled(is_true)
        self.bt_reward_left_open.setEnabled(is_true)
        self.bt_reward_left_close.setEnabled(is_true)
        self.bt_door_open.setEnabled(is_true)
        self.bt_door_close.setEnabled(is_true)
        self.bt_reward_right_open.setEnabled(is_true)
        self.bt_reward_right_close.setEnabled(is_true)
        self.bt_reward_right.setEnabled(is_true)
        self.bt_reward_left.setEnabled(is_true)
        self.txt_reward_left.setEnabled(is_true)
        self.txt_reward_right.setEnabled(is_true)

    def show_disc_wall(self, state: int):
        if state == 0:
            # Define to OPEN
            pixmap = QPixmap('images/disc-wall-open.png')
            self.lb_disc_wall.setPixmap(pixmap)
            self.lb_disc_wall_state.setText("OPEN")
        elif state == 1:
            # Define to CLOSE
            pixmap = QPixmap('images/disc-wall-closed.png')
            self.lb_disc_wall.setPixmap(pixmap)
            self.lb_disc_wall_state.setText("CLOSED")
        else:
            # Define to LARGE
            pixmap = QPixmap('images/disc-wall-large.png')
            self.lb_disc_wall.setPixmap(pixmap)
            self.lb_disc_wall_state.setText("LARGE")

    def show_door(self, state: int):
        if state == 0:
            pixmap = QPixmap('images/door-closed.png')
            self.lb_door.setPixmap(pixmap)
            self.lb_door_state.setText("CLOSED")
        else:
            pixmap = QPixmap('images/door-open.png')
            self.lb_door.setPixmap(pixmap)
            self.lb_door_state.setText("OPEN")

    def show_reward_left(self, state: int):
        if state == 0:
            pixmap = QPixmap('images/reward-closed.png')
            self.lb_reward_left.setPixmap(pixmap)
            self.lb_reward_left_state.setText("CLOSED")
        else:
            pixmap = QPixmap('images/reward-open.png')
            self.lb_reward_left.setPixmap(pixmap)
            self.lb_reward_left_state.setText("OPEN")

    def show_reward_right(self, state: int):
        if state == 0:
            pixmap = QPixmap('images/reward-closed.png')
            self.lb_reward_right.setPixmap(pixmap)
            self.lb_reward_right_state.setText("CLOSED")
        else:
            pixmap = QPixmap('images/reward-open.png')
            self.lb_reward_right.setPixmap(pixmap)
            self.lb_reward_right_state.setText("OPEN")

    def show_sensor(self, sensor: int, state: int):
        if state == 0 and self.list_sensors[sensor].last != state:
            pixmap = QPixmap('images/light-green.png')
            self.list_sensors[sensor].label.setPixmap(pixmap)
            self.list_sensors[sensor].last = state
            self.list_sensors[sensor].count = self.list_sensors[sensor].count + 1
            self.list_sensors[sensor].label_count.setText(str(self.list_sensors[sensor].count))
        elif self.list_sensors[sensor].last != state:
            pixmap = QPixmap('images/light-red.png')
            self.list_sensors[sensor].label.setPixmap(pixmap)
            self.list_sensors[sensor].last = state

    def show_reset(self):
        pixmap = QPixmap('images/disc-wall-open.png')
        self.lb_disc_wall.setPixmap(pixmap)

        pixmap = QPixmap('images/door-closed.png')
        self.lb_door.setPixmap(pixmap)

        pixmap = QPixmap('images/reward-closed.png')
        self.lb_reward_left.setPixmap(pixmap)
        self.lb_reward_right.setPixmap(pixmap)

        pixmap = QPixmap('images/light-gray.png')
        for sensor in self.list_sensors:
            sensor.count = 0
            sensor.last = 2
            sensor.label.setPixmap(pixmap)
            sensor.label_count.setText("0")

    # ----------------Thread functions----------------
    def thread_read_sensors(self):
        # print("Reading Serial...")
        if self.arduino_serial.is_connected():
            try:
                if self.arduino_serial.in_waiting():
                    txt = self.arduino_serial.read()
                    print("Reading: " + txt)
                    if txt == "p0=0":
                        self.show_sensor(0, 0)
                    elif txt == "p0=1":
                        self.show_sensor(0, 1)
                    elif txt == "p1=0":
                        self.show_sensor(1, 0)
                    elif txt == "p1=1":
                        self.show_sensor(1, 1)
                    elif txt == "p2=0":
                        self.show_sensor(2, 0)
                    elif txt == "p2=1":
                        self.show_sensor(2, 1)
                    elif txt == "p3=0":
                        self.show_sensor(3, 0)
                    elif txt == "p3=1":
                        self.show_sensor(3, 1)
            except SerialException:
                print(SerialException)
                # QMessageBox.warning(self, "Error", "Arduino was disconnected")
                self.bt_cmd_disconnect()
                self.bt_cmd_update()

        elif not self.bt_connect.isEnabled():
            self.bt_cmd_disconnect()
            self.bt_cmd_update()

    def connect_read_sensors(self, txt: str):
        # print("Reading Serial...")
        # print("Reading: " + txt)
        if txt == "p0=0":
            self.show_sensor(0, 0)
        elif txt == "p0=1":
            self.show_sensor(0, 1)
        elif txt == "p1=0":
            self.show_sensor(1, 0)
        elif txt == "p1=1":
            self.show_sensor(1, 1)
        elif txt == "p2=0":
            self.show_sensor(2, 0)
        elif txt == "p2=1":
            self.show_sensor(2, 1)
        elif txt == "p3=0":
            self.show_sensor(3, 0)
        elif txt == "p3=1":
            self.show_sensor(3, 1)


class SerialSensor:
    def __init__(self, label: QLabel, label_count: QLabel, count: int, last: 0):
        self.label = label
        self.label_count = label_count
        self.count = count
        self.last = last
