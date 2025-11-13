# Servo Control Library
# 11/13/25


# PUBLIC LIBRARIES
import pigpio


class Servo:
    def __init__(self, pi: pigpio.pi, pin: int, min_us: int = 1000, max_us: int = 2000, stop_us: int = 1500):
        self.pi = pi
        self.pin = pin

        self.min_us = min_us
        self.max_us = max_us
        self.stop_us = stop_us

        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.stop()

    def pulse(self, width):
        self.pi.set_servo_pulsewidth(self.pin, width)

    def stop(self):
        self.pulse(self.stop_us)

    def forward(self, speed):
        speed = max(0.0, min(1.0, speed))
        self.pulse(self.stop_us + speed*(self.max_us - self.stop_us))

    def reverse(self, speed):
        speed = max(0.0, min(1.0, speed))
        self.pulse(self.stop_us - speed*(self.stop_us - self.min_us))

    def shutdown(self):
        self.pi.set_servo_pulsewidth(self.pin, 0)