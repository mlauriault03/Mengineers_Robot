# Continous Servo Motor Test
# 11/3/25

import pigpio
import time
from servo import Servo

SIGNAL_PIN = 12


pi = pigpio.pi()
servo = Servo(pi, SIGNAL_PIN)

try:
    while True:
        print("Moving forward")
        servo.forward(0.5)
        time.sleep(2)

        print("Stopping")
        servo.stop()
        time.sleep(1)

        print("Reversing")
        servo.reverse(0.5)
        time.sleep(2)

        print("Stopping")
        servo.stop()
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    servo.shutdown()
    pi.stop()