# Servo Control Library
# 11/13/25


# PUBLIC LIBRARIES
import lgpio
import threading
import time



class Servo:
    """
    Continuous Servo Controller for Raspberry Pi 5 using lgpio.
    
    Speed range:
        -1.0 = full reverse
        0.0 = stop
        1.0 = full forward
    """

    # CONSTANTS
    
    PERIOD = 20000  # [us] 20ms period for 50 Hz


    # CONSTRUCTOR

    def __init__(self, pin: int, direction: int = 1, chip: int = 0,
        pulse_reverse: int = 1000,  # [us] full speed reverse
        pulse_forward: int = 2000,  # [us] full speed forward
        pulse_neutral: int = 1500   # [us] neutral/stop
    ):
        # Initialize servo parameters
        self.pin = pin
        self.direction = direction
        self.chip = chip
        self.pulse_reverse = pulse_reverse
        self.pulse_forward = pulse_forward
        self.pulse_neutral = pulse_neutral

        # Validate pin
        if pin != 12 and pin != 13:
            raise ValueError("Servo must use GPIO12 or GPIO13 on Raspberry Pi 5 (hardware PWM).")
        
        # PWM parameters
        self._speed = 0.0
        self._running = True
        self._lock = threading.Lock()

        # self.startup()

    
    # PRIVATE METHODS

    def _speed_to_pulse(self, speed):
        """Convert -1..+1 speed to pulse width."""
        if speed > 1.0:  speed = 1.0
        if speed < -1.0: speed = -1.0
        if speed > 0:
            return self.pulse_neutral + speed * (self.pulse_forward - self.pulse_neutral)
        else:
            return self.pulse_neutral + speed * (self.pulse_neutral - self.pulse_reverse)

    def _pulse_worker(self):
        """Thread that outputs 50 Hz servo pulses indefinitely."""
        while self._running:
            with self._lock:
                pulse = int(self._speed_to_pulse(self._speed))
            # High for pulse µs, then low for rest of 20ms
            lgpio.tx_pulse(self.h, self.pin, pulse, self.PERIOD - pulse)
            # Sleep 20ms to maintain 50 Hz
            time.sleep(0.020)


    # PUBLIC METHODS

    def startup(self):
        # Claim hardware
        self.h = lgpio.gpiochip_open(self.chip)
        lgpio.gpio_claim_output(self.h, self.pin)

        # Start the worker thread
        self.thread = threading.Thread(target=self._pulse_worker, daemon=True)
        self.thread.start()

    def set_speed(self, speed):
        """
        Set servo speed in range [-1, 1].
            -1 = full reverse
            0 = stop
            1 = full forward
        """
        with self._lock:
            self._speed = float(speed) * self.direction

    def stop(self):
        """Stop the servo and hold neutral."""
        self.set_speed(0.0)

    def shutdown(self):
        """Clean up thread and GPIO."""
        self._running = False
        self.thread.join()
        self.stop()
        # Send a few neutral pulses to settle
        for _ in range(5):
            lgpio.tx_pulse(self.h, self.pin, self.pulse_neutral, self.PERIOD - self.pulse_neutral)
            time.sleep(0.02)
        # Close chip controller
        lgpio.gpiochip_close(self.h)
        print("SERVO SHUT DOWN COMPLETE")