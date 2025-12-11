# Drive Controller Test
# 12/10/25



# PUBLIC LIBRARIES
import time


# PRIVATE LIBRARIES
from servo import Servo
from encoder import Encoder
from drive import Drive
from main import PIN_SERVO_LEFT, PIN_SERVO_RIGHT, ADDR_ENC_LEFT, ADDR_ENC_RIGHT



def test1():
    # Hardware control objects
    servo_left  = Servo(PIN_SERVO_LEFT, 1)
    servo_right = Servo(PIN_SERVO_RIGHT, -1)
    encoder_left = Encoder(ADDR_ENC_LEFT, 1)
    encoder_right = Encoder(ADDR_ENC_RIGHT, -1)

    servo_left.startup()
    servo_right.startup()

    servo_left.set_speed(1.0)
    servo_right.set_speed(1.0)

    time.sleep(3)

    servo_left.shutdown()
    servo_right.shutdown()
    
    time.sleep(2)


def test2():
    # Initialize drive controller
    d = Drive(PIN_SERVO_LEFT, PIN_SERVO_RIGHT, ADDR_ENC_LEFT, ADDR_ENC_RIGHT)

    print("Starting test...")
    d.move_forward(10) # do ticks for now

    print("Ending test...")


def tune_servo_pulses():
    servo = Servo(PIN_SERVO_RIGHT, -1,
        pulse_reverse = 1000,
        pulse_neutral = 1500,
        pulse_forward = 2000
    )
    # servo = Servo(PIN_SERVO_RIGHT, -1)
    speed_input = 0
    while True:
        speed_input = input("speed: ")
        if speed_input == 'q': break
        speed = float(speed_input)
        print(speed)
        servo.set_speed(speed)
    
    servo.stop()
    time.sleep(2)




# If this file is run as a script
if __name__ == "__main__":
    test2()