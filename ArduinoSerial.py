import serial
import serial.tools.list_ports


class ArduinoSerial:

    def __init__(self, *args):
        if len(args) == 0:
            self.created = False
        else:
            self.com_port = args[0]
            self.baud_rate = args[1]
            self.serial_port = serial.Serial(self.com_port, self.baud_rate, timeout=1)
            self.created = True

    def disconnect(self):
        self.serial_port.close()

    def send(self, txt: str):
        if txt[-1] != "\n":
            txt = txt + "\n"
        self.serial_port.write(str.encode(txt))

    def read(self):
        return self.serial_port.readline().decode().strip()

    def is_connected(self):
        if self.created:
            return self.serial_port.is_open & self.created
        else:
            return False

    def in_waiting(self):
        return self.serial_port.in_waiting

    @staticmethod
    def list_arduino_com_ports():
        arduino_ports = [
            p
            for p in serial.tools.list_ports.comports()
            # if 'Arduino' in p.description  # may need tweaking to match new arduino
        ]
        return arduino_ports
