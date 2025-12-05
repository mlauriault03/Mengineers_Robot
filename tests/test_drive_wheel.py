# Drive Wheel test
# 12/4/25


# PRIVATE LIBRARIES
from drive_wheel import DriveWheel
from main import PIN_SERVO_LEFT, PIN_SERVO_RIGHT, ADDR_ENC_LEFT, ADDR_ENC_RIGHT


def test1():
    left_wheel = DriveWheel(PIN_SERVO_LEFT, ADDR_ENC_LEFT)
    right_wheel = DriveWheel(PIN_SERVO_RIGHT, ADDR_ENC_RIGHT)

    left_wheel.start()
    right_wheel.start()

    left_wheel.set_target_position(500)
    right_wheel.set_target_position(500)


# If this file is run as a script
if __name__ == "__main__":
    test1()