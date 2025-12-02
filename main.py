# Main Robot Program
# 11/12/25

# PUBLIC LIBRARIES
from enum import Enum
from threading import Thread
import time
# TODO add drone control library

# PRIVATE LIBRARIES
from encoder import Encoder
from servo import Servo
from drive_wheel import DriveWheel
from arduino import Arduino, Command


# PARAMETERS
PORT_ARDUINO    = '/dev/ttyACM0'
PIN_SERVO_LEFT  = 13    # GPIO13 (PWM1)
PIN_SERVO_RIGHT = 12    # GPIO12 (PWM0)
ADDR_ENC_LEFT   = 0x37  # A0=HIGH, A1=LOW
ADDR_ENC_RIGHT  = 0x36  # A0=LOW, A1=LOW



# DATA STRUCTURES
# Robot states for state machine
class State(Enum):
    STOPPED     = 0     # Robot is stopped
    MOVING      = 1     # Robot is moving
    CRANK       = 2     # Turning crank paddle
    KEYPAD      = 3     # Turning keypad shaft
    BUTTON      = 4     # Running into button
    DUCK        = 5     # Knocking off duck
    DRONE       = 6     # Controlling drone
    RETURNING   = 7     # Returning to starting area


# ROBOT

class Robot:
    def __init__(self):
        self.state = State.STOPPED

        # Arduino communication
        self.arduino = Arduino(PORT_ARDUINO, 9600)

        # Hardware objects
        self.left_enc = Encoder(ADDR_ENC_LEFT)
        self.right_enc = Encoder(ADDR_ENC_RIGHT)
        self.left_servo = Servo(PIN_SERVO_LEFT)
        self.right_servo = Servo(PIN_SERVO_RIGHT)

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
            self.arduino.send_command(Command.MOTOR1)
            # TODO: wait for reponse from Arduino -> then change state
            pass
        elif self.state == State.KEYPAD:
            self.stop()
            self.arduino.send_command(Command.MOTOR2)
            # TODO: wait for reponse from Arduino -> then change state
            pass
        elif self.state == State.BUTTON:
            # TODO: run into the button
            # TODO: change state based on sensor inputs
            pass
        elif self.state == State.DUCK:
            self.stop()
            self.arduino.send_command(Command.MOTOR3)
            # TODO: wait for reponse from Arduino -> then change state
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