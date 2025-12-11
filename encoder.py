# Encoder Control Library
# 11/13/25


# PUBLIC LIBRARIES
import time
import threading
import board
import busio
from adafruit_seesaw import seesaw, rotaryio


class Encoder:
    """
    Adafruit I2C Rotary Encoder Interface
    Provides:
      - position (counts)
      - velocity (counts/sec)
      - optional threaded polling
    """
    
    # CONSTANTS

    TICKS_PER_REV = 24      # Ticks per full revolution
    DEFAULT_ADDR = 0x36     # I2C address without A0 or A1 set
    DEFAULT_RATE_HZ = 200   # polling frequency (5 ms)


    # CONSTRUCTOR

    def __init__(self, address: int = DEFAULT_ADDR, direction: int = 1, rate_hz: int = DEFAULT_RATE_HZ):
        # Allow user to pass an I2C bus or create one
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ss = seesaw.Seesaw(self.i2c, addr=address)
        self.encoder = rotaryio.IncrementalEncoder(self.ss)

        # Forward Spin Direction
        self.direction = direction

        # Thread state
        self.rate_hz = rate_hz
        self._running = False
        self._thread = None

        # Data
        self._position = 0
        self._velocity = 0.0
        self._last_position = 0
        self._last_time = time.time()

        # Lock for thread-safe access
        self._lock = threading.Lock()


    # PUBLIC METHODS

    def start(self):
        """Start background polling thread."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._update_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop background thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)

    def reset(self):
        """Reset position to zero."""
        with self._lock:
            # Seesaw allows writing a new position
            self.encoder.position = 0
            self._position = 0
            self._velocity = 0.0
            self._last_position = 0
            self._last_time = time.time()
        print("ENCODER RESET")

    def get_position(self):
        """Returns encoder count (thread-safe)."""
        with self._lock:
            return self._position

    def get_velocity(self):
        """Returns velocity (counts/sec)."""
        with self._lock:
            return self._velocity


    # PRIVATE METHODS

    def _update_loop(self):
        period = 1.0 / self.rate_hz

        # Initialize last values
        self._last_position = self.encoder.position
        self._last_time = time.time()

        while self._running:
            now = time.time()
            pos = self.encoder.position * self.direction

            dt = now - self._last_time
            dp = pos - self._last_position

            vel = dp / dt if dt > 1e-6 else 0.0

            with self._lock:
                self._position = pos
                self._velocity = vel

            self._last_position = pos
            self._last_time = now
            time.sleep(period)