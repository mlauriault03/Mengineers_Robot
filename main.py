# Main Robot Program
# 11/12/25

# PUBLIC LIBRARIES
from enum import Enum
# TODO add drone control library

# PRIVATE LIBRARIES
from drive_wheel import DriveWheel
from arduino import Arduino, Command


# PARAMETERS
PORT_ARDUINO    = '/dev/ttyACM0'
PIN_SERVO_LEFT  = 13    # GPIO13 (PWM1)
PIN_SERVO_RIGHT = 12    # GPIO12 (PWM0)
ADDR_ENC_LEFT   = 0x37  # A0=HIGH, A1=LOW
ADDR_ENC_RIGHT  = 0x36  # A0=LOW, A1=LOW

# COORDINATES
XY_START     = (0, 0)
XY_KEYPAD    = (0, 0)
XY_DUCK      = (0, 0)
XY_BUTTON    = (0, 0)
XY_CRANK     = (0, 0)



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
        self.left_wheel = DriveWheel(PIN_SERVO_LEFT, ADDR_ENC_LEFT, 1)
        self.right_wheel = DriveWheel(PIN_SERVO_RIGHT, ADDR_ENC_RIGHT, -1)

    def start(self):
        """Start robot systems."""
        self.left_wheel.start()
        self.right_wheel.start()

    def shutdown(self):
        """Shutdown robot systems."""
        self.arduino.close()
        self.left_wheel.stop()
        self.right_wheel.stop()


    # TASK PROCEDURES

    def turn_crank(self):
        """Execute crank procedure."""
        self.state = State.CRANK
        self.stop()
        self.arduino.send_command(Command.MOTOR1)
        # TODO: wait for reponse from Arduino -> then change state

    def press_keypad(self):
        """Execute keypad procedure."""
        self.state = State.KEYPAD
        self.stop()
        self.arduino.send_command(Command.MOTOR2)
        # TODO: wait for reponse from Arduino -> then change state

    def push_button(self):
        """Execute button procedure."""
        self.state = State.BUTTON
        self.stop()
        # TODO: run into the button
        # TODO: change state based on sensor inputs

    def whack_duck(self):
        """Execute duck procedure."""
        self.state = State.DUCK
        self.stop()
        self.arduino.send_command(Command.MOTOR3)
        # TODO: wait for reponse from Arduino -> then change state

    def fly_drone(self):
        """Execute drone procedure."""
        self.state = State.DRONE
        self.stop()
        # TODO: send commands to drone
        # TODO: change state based on sensor inputs


    # MOVEMENT PROCEDURES

    def move_to(self, xy_target: tuple[float, float]):
        """Move robot to specified (x,y) location."""
        self.state = State.MOVING
        # TODO: implement navigation logic to move to (x, y) target
    
    def turn_by(self, angle_deg: float):
        """Turn robot by specified angle (degrees)."""
        self.state = State.MOVING
        # TODO: implement turning logic

    def stop(self):
        """Stop both drive wheels."""
        self.state = State.STOPPED
        self.left_wheel.stop()
        self.right_wheel.stop()

    
    # MAIN PROCEDURE

    def run(self):
        """Main robot procedure."""
        # sense flash signal
        # TODO
        # backup to wall to align direction
        # TODO
        # move to keypad
        self.move_to(XY_KEYPAD)
        # press keypad
        self.press_keypad()
        # move to duck
        self.move_to(XY_DUCK)
        # whack duck
        self.whack_duck()
        # move to button
        self.move_to(XY_BUTTON)
        # push button
        self.push_button()
        # move to crank
        self.move_to(XY_CRANK)
        # turn crank
        self.turn_crank()
        # fly drone
        self.fly_drone()
        # return to start (go around other side of crater - extra points)
        self.move_to(XY_START)
        


# Main Program
def main():
    # create robot instance
    robot = Robot()
    # start up
    robot.start()
    # run main procedure
    robot.run()
    # shut down
    robot.shutdown()


# If this file is executed as a script
if __name__ == "__main__":
    main()
