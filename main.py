# Main Robot Program
# 11/12/25

# PUBLIC LIBRARIES
import time
import math
from enum import Enum
# TODO add drone control library

# PRIVATE LIBRARIES
from drive import Drive
from encoder import Encoder
from arduino import Arduino, Command


# HARDWARE PARAMETERS
PORT_ARDUINO    = '/dev/ttyACM0'
PIN_SERVO_LEFT  = 13    # GPIO13 (PWM1)
PIN_SERVO_RIGHT = 12    # GPIO12 (PWM0)
ADDR_ENC_LEFT   = 0x37  # A0=HIGH, A1=LOW
ADDR_ENC_RIGHT  = 0x36  # A0=LOW, A1=LOW

# PID PARAMETERS
KP = 0.5                # Proportional (P) gain
KI = 0.0                # Integral (I) gain
KD = 0.0                # Derivative (D) gain


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
        # Drive wheel controllers (PID controlled)
        self.drive = Drive(PIN_SERVO_LEFT, PIN_SERVO_RIGHT, ADDR_ENC_LEFT, ADDR_ENC_RIGHT)


    # TASK PROCEDURES

    def turn_crank(self):
        """Execute crank procedure."""
        self.state = State.CRANK
        self.arduino.send_command(Command.MOTOR1)
        # TODO: wait for reponse from Arduino -> then change state

    def press_keypad(self):
        """Execute keypad procedure."""
        self.state = State.KEYPAD
        self.arduino.send_command(Command.MOTOR2)
        # TODO: wait for reponse from Arduino -> then change state

    def push_button(self):
        """Execute button procedure."""
        self.state = State.BUTTON
        self.drive.move_forward(-1)     # move back
        self.drive.move_forward(1)      # hit button 2nd time
        self.drive.move_forward(-1)     # move back
        self.drive.move_forward(1)      # hit button 3rd time
        self.state = State.MOVING

    def whack_duck(self):
        """Execute duck procedure."""
        self.state = State.DUCK
        self.arduino.send_command(Command.MOTOR3)
        # TODO: wait for reponse from Arduino -> then change state

    def fly_drone(self):
        """Execute drone procedure."""
        self.state = State.DRONE
        # TODO: send commands to drone
        # TODO: change state based on sensor inputs


    # MAIN PROCEDURE

    def run(self):
        """Main robot procedure."""
        # sense flash signal
        # TODO
        # backup to wall to align direction
        # TODO
        # move to button
        self.drive.move_forward(26)
        # push button
        self.push_button()
        # move to crank
        self.drive.move_forward(-14)
        self.drive.turn(90)
        self.drive.move_forward(32)
        self.drive.turn(-90)
        self.drive.move_forward(21)
        self.drive.turn(90)
        self.drive.move_forward(36)
        self.drive.turn(90)
        self.drive.move_forward(10)
        self.drive.turn(-90)
        self.drive.move_forward(12)
        self.drive.turn(-90)
        self.drive.move_forward(2)
        # turn crank
        self.turn_crank()
        # whack duck
        # self.whack_duck()
        # press keypad
        # self.press_keypad()
        # fly drone
        # self.fly_drone()
        # return to start (go around other side of crater - extra points)



# MAIN PROGRAM

def main():
    # create robot instance
    robot = Robot()
    # run main procedure
    robot.run()


# If this file is executed as a script
if __name__ == "__main__":
    main()
