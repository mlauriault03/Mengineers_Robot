# Functionality Demo Procedure
# 11/21/25


# PUBLIC LIBRARIES
import time

# PRIVATE LIBRARIES
from servo import Servo
from arduino import Arduino, Command

# PARAMETERS
PORT_ARDUINO    = '/dev/ttyACM0'
PIN_SERVO_LEFT  = 13    # GPIO13 (PWM1)
PIN_SERVO_RIGHT = 12    # GPIO12 (PWM0)


# left forward = positive speed
# right forward = negative speed


def demo():

    # Arduino communication
    arduino = Arduino(PORT_ARDUINO, 9600)

    # Hardware objects
    left_servo = Servo(PIN_SERVO_LEFT)
    right_servo = Servo(PIN_SERVO_RIGHT)

    print("Starting demo...")

    # Move forward and back
    print("Forward...")
    left_servo.set_speed(1.0)
    right_servo.set_speed(-1.0)
    time.sleep(1)
    print("Stop...")
    left_servo.set_speed(0.0)
    right_servo.set_speed(0.0)
    time.sleep(1)
    print("Reverse...")
    left_servo.set_speed(-1.0)
    right_servo.set_speed(1.0)
    time.sleep(1)
    print("Stop...")
    left_servo.set_speed(0.0)
    right_servo.set_speed(0.0)
    time.sleep(1)

    # Turn right in place
    print("Turn right...")
    left_servo.set_speed(1.0)
    right_servo.set_speed(1.0)
    time.sleep(6.0)
    print("Stop...")
    left_servo.set_speed(0.0)
    right_servo.set_speed(0.0)
    time.sleep(1)

    # Turn left in place
    print("Turn left...")
    left_servo.set_speed(-1.0)
    right_servo.set_speed(-1.0)
    time.sleep(6.0)
    print("Stop...")
    left_servo.set_speed(0.0)
    right_servo.set_speed(0.0)
    time.sleep(1)

    # Shutdown servos
    left_servo.shutdown()
    right_servo.shutdown()

    # Wait for user input to proceed
    input("Press any key to continue to keypad...")

    # Turn motor 1 (keypad)
    print("Activating motor 1 (keypad) through Arduino...")
    arduino.send_command(Command.MOTOR1)
    time.sleep(10)

    # Wait for user input to proceed
    input("Press any key to continue to crank...")

    # Turn motor 2 (crank)
    print("Activating motor 2 (crank) through Arduino...")
    arduino.send_command(Command.MOTOR2)
    time.sleep(10)
    
    # Wait for user input to proceed
    input("Press any key to continue to extender...")

    # Turn motor 3 (extender)
    print("Activating motor 3 (extender) through Arduino...")
    arduino.send_command(Command.MOTOR3)
    time.sleep(10)

    print("Demo complete.")



# If this file is executed as a script
if __name__ == "__main__":
    demo()