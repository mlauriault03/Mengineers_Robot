# Drive Wheel test
# 12/4/25


# PRIVATE LIBRARIES
from drive_wheel import DriveWheel
from main import PIN_SERVO_LEFT, PIN_SERVO_RIGHT, ADDR_ENC_LEFT, ADDR_ENC_RIGHT, KP, KI, KD


# PARAMETERS
TARGET_POS = 50


def test1():
    try:
        left_wheel = DriveWheel(PIN_SERVO_LEFT, ADDR_ENC_LEFT, 1, KP, KI, KD)
        right_wheel = DriveWheel(PIN_SERVO_RIGHT, ADDR_ENC_RIGHT, -1, KP, KI, KD)

        left_wheel.set_target_position(TARGET_POS)
        right_wheel.set_target_position(TARGET_POS)

        print("Starting drive wheels...")

        left_wheel.start()
        right_wheel.start()

        input("Press any key to end test...") # holds main thread so that control thread doesn't join
    except Exception as e:
        print(f"Error: {e.with_traceback()}")
    finally:
        print("Stopping...")
        left_wheel.stop()
        right_wheel.stop()
        print("Shutting down...")
        left_wheel.shutdown()
        right_wheel.shutdown()


def test2():
    try:
        left_wheel = DriveWheel(PIN_SERVO_LEFT, ADDR_ENC_LEFT, 1, KP, KI, KD)
        right_wheel = DriveWheel(PIN_SERVO_RIGHT, ADDR_ENC_RIGHT, -1, KP, KI, KD)

        left_wheel.turn_by(TARGET_POS)
        right_wheel.turn_by(TARGET_POS)

        print("Starting drive wheels...")

        left_wheel.start()
        right_wheel.start()

        input("Press any key to end test...") # holds main thread so that control thread doesn't join
    except Exception as e:
        print(f"Error: {e.with_traceback()}")
    finally:
        print("Stopping...")
        left_wheel.stop()
        right_wheel.stop()
        print("Shutting down...")
        left_wheel.shutdown()
        right_wheel.shutdown()


# If this file is run as a script
if __name__ == "__main__":
    test2()