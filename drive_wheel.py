# Drive Wheel Control Library
# 11/13/25


# PUBLIC LIBRARIES
import time
import threading


# PRIVATE LIBRARIES
from encoder import Encoder
from servo import Servo



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


class DriveWheel:
    """
    Robot Drive Wheel Controller. Provides:
    - Position control via PID
    - Velocity and position sensing via Encoder
    - Motor actuation via Servo
    Parameters:
    ----------
    servo_pin : int
        Servo GPIO pin number on the Raspberry PI
    encoder_addr : int
        Encoder I2C address
    direction : int
        Forward spin direction of wheel (1 = left wheel, -1 = right wheel)
    kp : float
        Proportional (P) gain coefficient
    ki : float
        Integral (I) gain coefficient
    kd : float
        Derivative (D) gain coefficient
    rate_hz : int
        Update rate in Hz
    """

    def __init__(self, servo_pin: int, encoder_addr: int, direction=1, kp=0.5, ki=0.0, kd=0.0, rate_hz=100):
        # Hardware control objects
        self.servo = Servo(servo_pin, direction)
        self.encoder = Encoder(encoder_addr, direction)
        # Forward Spin Direction
        self.direction = direction
        # PID controller
        self.pid = PID(kp, ki, kd, -1.0, 1.0)
        # Control state
        self.target_position = 0.0
        self.rate_hz = rate_hz
        # Threading
        self._running = False
        self._thread = None
        self._lock = threading.Lock()


    # PUBLIC METHODS

    def start(self):
        self.encoder.start()
        self._running = True
        self._thread = threading.Thread(target=self._control_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self.servo.stop()
        self.encoder.stop()

    def shutdown(self):
        self.stop()
        self.servo.shutdown()

    def set_target_position(self, pos):
        with self._lock:
            self.target_position = float(pos)
            self.pid.reset()

    def get_position(self):
        return self.encoder.get_position()

    def get_velocity(self):
        return self.encoder.get_velocity()


    # INTERNAL CONTROL LOOP

    def _control_loop(self):
        period = 1.0 / self.rate_hz
        while self._running:
            # Read encoder
            current_pos = self.encoder.get_position()
            # Get target safely
            with self._lock:
                target = self.target_position
            # Compute PID speed command
            speed_cmd = self.pid.update(target, current_pos)
            # If error is within 1 encoder tick -> target reached
            if abs(target - current_pos) < 1.0:
                # Stop servo (error is as small as possible)
                self.servo.set_speed(0.0)
                print("Target reached. Servo stopped.")
            # Otherwise keep trying to reduce error (reach target)
            else:
                # Set servo speed
                self.servo.set_speed(speed_cmd)
                print(f"{'LEFT' if self.direction == 1 else 'RIGHT'}:\ttarget: {target}\tposition: {current_pos}\tspeed: {speed_cmd}\t")
            # Wait for next cycle
            time.sleep(period)