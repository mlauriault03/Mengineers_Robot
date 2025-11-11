# Encoder Control Library
# 11/13/25


# PUBLIC LIBRARIES
import pigpio


class Encoder:
    def __init__(self, pi: pigpio.pi, pin_a: int, pin_b: int):
        self.pi = pi
        self.pin_a = pin_a
        self.pin_b = pin_b

        self.position = 0

        # Configure pins
        self.pi.set_mode(self.pin_a, pigpio.INPUT)
        self.pi.set_mode(self.pin_b, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin_a, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.pin_b, pigpio.PUD_UP)

        # Register callbacks
        self.cb_a = self.pi.callback(self.pin_a, pigpio.EITHER_EDGE, self._decode)
        self.cb_b = self.pi.callback(self.pin_b, pigpio.EITHER_EDGE, self._decode)

        # Last states
        self.last_a = self.pi.read(self.pin_a)
        self.last_b = self.pi.read(self.pin_b)

    def _decode(self, gpio, level, tick):
        """
        Decode quadrature transitions.
        This method is automatically called on every edge.
        """
        a = self.pi.read(self.pin_a)
        b = self.pi.read(self.pin_b)

        # Determine direction
        if gpio == self.pin_a:
            if level == 1:  # rising edge on A
                self.position += 1 if b == 0 else -1
            else:           # falling edge on A
                self.position += -1 if b == 0 else 1

        elif gpio == self.pin_b:
            if level == 1:  # rising edge on B
                self.position += -1 if a == 0 else 1
            else:           # falling edge on B
                self.position += 1 if a == 0 else -1

        # Save last state
        self.last_a = a
        self.last_b = b

    # -----------------------
    # Public API
    # -----------------------

    def get_position(self):
        """Return current encoder tick count."""
        return self.position

    def reset(self):
        """Zero the encoder count."""
        self.position = 0

    def stop(self):
        """Cleanly stop encoder callbacks."""
        self.cb_a.cancel()
        self.cb_b.cancel()