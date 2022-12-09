import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QTableWidgetItem, QStatusBar
from PyQt5.uic import loadUi

from ProjectObjects import TrainingExperiment


def hhmmss(ms):
    return time.strftime("%H:%M:%S", time.gmtime(ms/1000))


class UiVisualizeResultDialog(QDialog):

    closed = QtCore.pyqtSignal()

    def __init__(self, experiment: TrainingExperiment):
        super(UiVisualizeResultDialog, self).__init__()
        loadUi("window_visualize_result_play.ui", self)
        self.setWindowTitle("Visualize Experiment Results")
        self.setWindowIcon(QIcon("images/icon.png"))

        # self.bt_close.setIcon(QIcon("images/baseline_cancel_white_24dp.png"))
        self.bt_play.setIcon(QIcon("images/play-black.png"))
        self.bt_pause.setIcon(QIcon("images/pause-black.png"))
        self.bt_stop.setIcon(QIcon("images/stop-black.png"))
        # self.bt_close.clicked.connect(self.close)

        # Create Status Bar
        layout = QVBoxLayout()
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        self.frame_status_bar.setLayout(layout)
        self.status_bar.showMessage("Starting Experiment...")

        # Create log list
        self.list_log = []
        for log in experiment.log_list:
            log.timestamp = log.timestamp - experiment.time_start
            self.list_log.append(log)

        # Show all the information about the experiment on QLineEdits
        self.experiment = experiment
        self.txt_animal.setText("Name: " + experiment.animal.name + "\n" +
                                "Weight: " + str(experiment.animal.weight) + "\n" +
                                "Birth: " + experiment.animal.birth.strftime("%Y-%m-%d %H:%M:%S"))
        self.txt_program.setText("Name: " + experiment.program.name + "\n" +
                                 "Reward (ms): " + str(experiment.program.reward_ms) + "\n" +
                                 "Total Time: " + time.strftime("%H:%M:%S", time.gmtime(experiment.program.total_time)))
        self.txt_time_start.setText(experiment.time_start.strftime("%Y-%m-%d %H:%M:%S"))
        self.txt_time_end.setText(experiment.time_end.strftime("%Y-%m-%d %H:%M:%S"))
        self.txt_left.setText(str(experiment.left_success) + " / " + str(experiment.left_total))
        self.txt_right.setText(str(experiment.right_success) + " / " + str(experiment.right_total))
        success_percentage = 100 * (experiment.right_success + experiment.left_success) \
                             / (experiment.right_total + experiment.left_total)
        self.txt_total.setText(str(success_percentage) + " %")

        # Initiate Program Table
        self.disc_type = ['Closed', 'Wide', 'Open', 'Random']
        self.nose_success = ['Left', 'Right']
        self.nose_success_random = ["Closed - Left, Wide - Right", "Closed - Right, Wide - Left"]
        self.table_disc.setColumnCount(3)
        self.table_disc.setHorizontalHeaderLabels(["Disc Type", "Nose Success", "Time (s)"])
        self.table_disc.setColumnWidth(0, 70)
        self.table_disc.setColumnWidth(1, 70)
        self.table_disc.setColumnWidth(2, 40)
        header = self.table_disc.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        row = 0
        self.list_disc = self.experiment.program.disc_list
        self.table_disc.setRowCount(len(self.list_disc))
        for disc in self.list_disc:
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
            row += 1

        # Create widgets to add to existing frame on Ui
        self.video_widget0 = QVideoWidget()
        self.video_layout0 = QVBoxLayout()
        self.video_layout0.setContentsMargins(0, 0, 0, 0)
        self.video_layout0.addWidget(self.video_widget0)
        self.frame_video0.setLayout(self.video_layout0)
        # Creating the Player (QMediaPlayer Object)
        self.playing_two = False
        self.rate0 = 1
        self.rate1 = 1
        self.player0 = QMediaPlayer()
        self.player0.setVideoOutput(self.video_widget0)
        self.player0.error.connect(self.error_alert)
        self.player0.positionChanged.connect(self.update_position)
        self.player0.durationChanged.connect(self.duration_changed)
        self.player0.setMedia(QMediaContent(QUrl.fromLocalFile(self.experiment.resource_list[0].link)))
        # Connect buttons to player
        self.bt_play.pressed.connect(self.player0.play)
        self.bt_pause.pressed.connect(self.player0.pause)
        self.bt_stop.pressed.connect(self.player0.stop)
        self.slider_time.valueChanged.connect(self.update_player_position)

        # Check if there are two videos
        if len(experiment.resource_list) > 1:
            # Do the same for second player
            self.playing_two = True
            self.video_widget1 = QVideoWidget()
            self.video_layout1 = QVBoxLayout()
            self.video_layout1.setContentsMargins(0, 0, 0, 0)
            self.video_layout1.addWidget(self.video_widget1)
            self.frame_video1.setLayout(self.video_layout1)

            self.player1 = QMediaPlayer()
            self.player1.setVideoOutput(self.video_widget1)
            self.player1.error.connect(self.error_alert)
            self.player1.durationChanged.connect(self.duration_changed_second)
            self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(self.experiment.resource_list[1].link)))
            self.bt_play.pressed.connect(self.player1.play)
            self.bt_pause.pressed.connect(self.player1.pause)
            self.bt_stop.pressed.connect(self.player1.stop)
            self.bt_stop.pressed.connect(self.bt_cmd_stop)

    def bt_cmd_stop(self):
        self.status_bar.showMessage("Starting Experiment...")

    def update_player_position(self, position):
        self.player0.setPosition(position * self.rate0)
        if self.playing_two:
            self.player1.setPosition(position * self.rate1)

    def update_position(self, position):
        self.lb_current_time.setText(hhmmss(position / self.rate0))
        self.slider_time.blockSignals(True)
        self.slider_time.setValue(position / self.rate0)
        self.slider_time.blockSignals(False)
        self.show_log(position / self.rate0)

    def duration_changed(self, duration):
        self.lb_total_time.setText(hhmmss(self.experiment.program.total_time*1000))
        self.rate0 = duration / (1000 * self.experiment.program.total_time)
        self.player0.setPlaybackRate(self.rate0)
        self.slider_time.setRange(0, self.experiment.program.total_time*1000)

    def duration_changed_second(self, duration):
        self.rate1 = duration / (1000 * self.experiment.program.total_time)
        self.player1.setPlaybackRate(self.rate1)

    def error_alert(self, *args):
        print(args)
        QMessageBox.critical(self, "ERROR", "Video files not found")

    def show_log(self, position_ms):
        seconds = position_ms/1000
        # print("Position = " + str(seconds))
        i = 0
        for log in self.list_log:
            # print("Total Seconds = " + str(log.timestamp.total_seconds()))
            if log.timestamp.total_seconds() >= seconds:
                i = i - 1
                break
            if i == (len(self.list_log) - 1):
                break
            i += 1
        if i >= 0:
            self.status_bar.showMessage(self.list_log[i].log_text)

    def closeEvent(self, a0):
        self.closed.emit()  # Send signal to other window that this one is closing
