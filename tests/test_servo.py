# Continous Servo Motor Test
# 11/3/25


# PUBLIC LIBRARIES
import time
from servo import Servo


# TEST PARAMETERS
SIGNAL_PIN = 12


# MAIN TEST
servo = Servo(pin=SIGNAL_PIN)

print("Moving forward")
servo.forward(0.5)
time.sleep(2)

print("Reversing")
servo.reverse(1.0)
time.sleep(2)

print("Stopping")
servo.stop()
servo.shutdown()
