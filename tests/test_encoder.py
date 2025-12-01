# Encoder test
# 11/20/25


# PUBLIC LIBRARIES
import time
import board
import busio
from adafruit_seesaw import seesaw, rotaryio


# PRIVATE LIBRARIES
# from encoder import Encoder


# PARAMETERS
I2C_ADDR = 0x36         # default address


def test1():
    """Test encoder basic functionality."""
    print("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)

    print("Connecting to encoder...")
    ss = seesaw.Seesaw(i2c, addr=I2C_ADDR)

    # Create encoder object
    enc = rotaryio.IncrementalEncoder(ss)

    print("Encoder initialized. Rotate the knob.\n")

    last = enc.position

    while True:
        pos = enc.position
        if pos != last:
            print(f"Position: {pos}")
            last = pos
        time.sleep(0.01)


def test2():
    """Test custom Encoder library"""
    # TODO
    pass


# If this file is run as a script
if __name__ == "__main__":
    test1()
