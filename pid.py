# General PID Controller
# 12/10/25


# PUBLIC LIBRARIES
import time



class PID:
    """Minimal PID controller for robotic control loops."""
    def __init__(self, kp, ki, kd, output_min=-1.0, output_max=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min = output_min
        self.out_max = output_max

        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

    def update(self, target, current):
        now = time.time()
        dt = now - self.last_time
        if dt <= 0:
            dt = 1e-6

        error = target - current

        # PID components
        p = self.kp * error
        self.integral += error * dt
        i = self.ki * self.integral
        d = self.kd * (error - self.last_error) / dt

        output = p + i + d

        # Clamp output
        output = max(self.out_min, min(self.out_max, output))

        # Store
        self.last_error = error
        self.last_time = now

        return output