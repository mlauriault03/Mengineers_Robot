# Main Robot Program
# 11/12/25

# PUBLIC LIBRARIES
from enum import Enum
from threading import Thread
import pigpio
import time
# TODO add drone control library

# PRIVATE LIBRARIES
from encoder import Encoder
from servo import Servo
from drive_wheel import DriveWheel


# PARAMETERS
PIN_LEFT_SERVO      = 0
PIN_RIGHT_SERVO     = 0
PIN_LEFT_ENC_A      = 0
PIN_LEFT_ENC_B      = 0
PIN_RIGHT_ENC_A     = 0
PIN_RIGHT_ENC_B     = 0


# DATA STRUCTURES
# Robot states for state machine
class State(Enum):
    STOPPED = 0             # Robot is stopped
    MOVING = 1              # Robot is moving
    CRANK = 2               # Turning crank paddle
    KEYPAD = 3              # Turning keypad shaft
    BUTTON = 4              # Running into button
    DUCK = 5                # Knocking off duck
    DRONE = 6               # Controlling drone
    RETURNING = 8           # Returning to starting area


# ROBOT

class Robot:
    def __init__(self):
        self.state = State.STOPPED
        self.pi = pigpio.pi()

        # Hardware objects
        self.left_enc = Encoder(self.pi, PIN_LEFT_ENC_A, PIN_LEFT_ENC_B)
        self.right_enc = Encoder(self.pi, PIN_RIGHT_ENC_A, PIN_RIGHT_ENC_B)
        self.left_servo = Servo(self.pi, PIN_LEFT_SERVO)
        self.right_servo = Servo(self.pi, PIN_RIGHT_SERVO)

        # Drive wheels (PID controlled)
        self.left_wheel = DriveWheel(self.left_servo, self.left_enc)
        self.right_wheel = DriveWheel(self.right_servo, self.right_enc)

    def update_state(self):
        """State Machine Logic"""
        if self.state == State.STOPPED:
            self.stop()
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.MOVING:
            # TODO: navigation logic (use PID controller for each drive motor)
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.CRANK:
            self.stop()
            # TODO: send command to Arduino via pyserial to turn motor
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.KEYPAD:
            self.stop()
            # TODO: send command to Arduino via pyserial to turn motor
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.BUTTON:
            # TODO: run into the button
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.DUCK:
            self.stop()
            # TODO: send command to Arduino via pyserial to turn motor
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.DRONE:
            self.stop()
            # TODO: send commands to drone
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.RETURNING:
            # TODO: return to starting area
            # TODO: change state based on sensor inputs
            pass
        else:
            # TODO unknown state
            pass

    def stop(self):
        """Stop both drive wheels."""
        self.left_wheel.stop()
        self.right_wheel.stop()


# Main program loop
def main():
    robot = Robot()
    # State machine loop (main thread)
    while True:
        robot.update_state()
        robot.left_wheel.update()
        robot.right_wheel.update()
        time.sleep(0.01)


# If this file is executed as a script
if __name__ == "__main__":
    main()