# Main Robot Program
# 11/12/25

# PUBLIC LIBRARIES
from enum import Enum
from threading import Thread
# TODO add servo control library
# TODO add drone library


# PARAMETERS
PIN_LEFT_SERVO      = 0
PIN_RIGHT_SERVO     = 0
PIN_LEFT_ENCODER    = 0
PIN_RIGHT_ENCODER   = 0


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


# GLOBAL VARIABLES
state: State = None         # Current state of the robot


# LISTENER HANDLERS
def left_encoder_listener():
    pass
def right_encoder_listener():
    pass


# LISTENER THREADS
# TODO: implement sensor and input listener threads
left_encoder_thread = Thread(target=left_encoder_listener)
right_encoder_thread = Thread(target=right_encoder_listener)


# State Machine Logic
def update_state():
    if state == State.STOPPED:
        # TODO: set speed of both drive motors to zero
        # TODO: change state based on sensor inputs
        pass
    elif state == State.MOVING:
        # TODO: navigation logic (use PID controller for each drive motor)
        # TODO: change state based on sensor inputs
        pass
    elif state == State.CRANK:
        # TODO: send command to Arduino via pyserial to turn motor
        # TODO: change state based on sensor inputs
        pass
    elif state == State.KEYPAD:
        # TODO: send command to Arduino via pyserial to turn motor
        # TODO: change state based on sensor inputs
        pass
    elif state == State.BUTTON:
        # TODO: run into the button
        # TODO: change state based on sensor inputs
        pass
    elif state == State.DUCK:
        # TODO: send command to Arduino via pyserial to turn motor
        # TODO: change state based on sensor inputs
        pass
    elif state == State.DRONE:
        # TODO: send commands to drone
        # TODO: change state based on sensor inputs
        pass
    elif state == State.RETURNING:
        # TODO: return to starting area
        # TODO: change state based on sensor inputs
        pass
    else:
        # TODO unknown state
        pass


# Main program loop
def main():
    # Start listener threads
    left_encoder_thread.start()
    right_encoder_thread.start()
    # Set initial state
    state = State.STOPPED
    # State machine loop (main thread)
    while True:
        # Update state
        update_state()


# If this file is executed as a script
if __name__ == "__main__":
    main()