# Continous Servo Test
# 11/3/25


from gpiozero import Servo # sudo apt install python3-gpiozero
from time import sleep

servo = Servo(17, min_pulse_width=0.0009, max_pulse_width=0.0021)

def test_servo():
    print("Testing continuous rotation servo...")

    # Full speed clockwise
    print("Full speed clockwise")
    servo.max()
    sleep(2)

    # Stop
    print("Stop")
    servo.mid()
    sleep(1)

    # Full speed counterclockwise
    print("Full speed counterclockwise")
    servo.min()
    sleep(2)

    # Stop again
    print("Stop")
    servo.mid()
    sleep(1)

    print("Test complete.")

try:
    test_servo()
except KeyboardInterrupt:
    servo.mid()
    print("\nStopped by user.")