# Arduino Communication Interface
# 11/17/25


import serial
import time
from enum import Enum


class Command(str, Enum):
    MOTOR1 = "MOTOR1"
    MOTOR2 = "MOTOR2"
    MOTOR3 = "MOTOR3"
    

class Arduino:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Allow Arduino to reset

    def send_command(self, command: Command):
        """Send a command string to the Arduino."""
        self.ser.write((command + '\n').encode())

    def read_response(self):
        """Read a line of response from the Arduino."""
        if self.ser.in_waiting > 0:
            return self.ser.readline().decode().strip()
        return None

    def close(self):
        """Close the serial connection."""
        self.ser.close()