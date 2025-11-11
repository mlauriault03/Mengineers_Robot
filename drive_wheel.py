# Drive Wheel Control Library
# 11/13/25


# PUBLIC LIBRARIES
import time


# PRIVATE LIBRARIES
from encoder import Encoder
from servo import Servo



class DriveWheel:
    """
    Combines a continuous servo + encoder + simple PID controller.
    """

    def __init__(self, servo: Servo, encoder: Encoder, kp=0.4, kd=0.0):
        self.servo = servo
        self.encoder = encoder
        self.kp = kp
        self.kd = kd

        self.target_pos = None
        self.last_error = 0
        self.last_time = time.time()

    # -----------------------------
    # Open-loop control
    # -----------------------------
    def set_speed(self, speed):
        if speed > 0:
            self.servo.forward(speed)
        elif speed < 0:
            self.servo.reverse(abs(speed))
        else:
            self.servo.stop()

    # -----------------------------
    # Closed-loop position control
    # -----------------------------
    def go_to(self, target_pos):
        """
        Set a target encoder tick position.
        """
        self.target_pos = target_pos

    def update(self):
        """
        Update PID loop. Call this every time Robot.update_state() runs.
        """
        if self.target_pos is None:
            return

        pos = self.encoder.get_position()
        error = self.target_pos - pos

        # Deadband
        if abs(error) < 2:
            self.servo.stop()
            return

        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        derivative = (error - self.last_error) / dt if dt > 0 else 0
        self.last_error = error

        cmd = self.kp * error + self.kd * derivative

        # clamp output
        cmd = max(-1.0, min(1.0, cmd))

        self.set_speed(cmd)

    def stop(self):
        self.servo.stop()
        self.target_pos = None