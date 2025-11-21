# Encoder test
# 11/20/25


# PUBLIC LIBRARIES
import time
import board
import busio
from adafruit_seesaw.seesaw import Seesaw


# PRIVATE LIBRARIES
# from encoder import Encoder


# PARAMETERS
I2C_ADDR = 0x36         # default address


def test1():
    """Test encoder basic functionality."""
    print("Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)

    print("Connecting to encoder...")
    ss = Seesaw(i2c, addr=I2C_ADDR)

    # Enable encoder
    ss.encoder_enable()
    ss.set_encoder_position(0)

    print("Encoder initialized.")
    print("Rotate the knob. Press Ctrl+C to exit.\n")

    last = ss.encoder_position

    while True:
        pos = ss.encoder_position
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