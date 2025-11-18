# Servo Control Library
# 11/13/25


# PUBLIC LIBRARIES
import time
import os


class HardwarePWM:
    """
    Simple wrapper around /sys/class/pwm PWM interface.
    Uses pwmchip0 for Raspberry Pi 5 (GPIO12/13).
    """

    def __init__(self, chip: int, channel: int):
        self.chip = chip
        self.channel = channel
        self.base = f"/sys/class/pwm/pwmchip{chip}"
        self.path = f"{self.base}/pwm{channel}"

        # Export PWM channel if needed
        if not os.path.exists(self.path):
            with open(f"{self.base}/export", "w") as f:
                f.write(str(channel))
            time.sleep(0.1)  # allow sysfs to populate

    def enable(self, value: bool):
        with open(f"{self.path}/enable", "w") as f:
            f.write("1" if value else "0")

    def set_period(self, period_ns: int):
        with open(f"{self.path}/period", "w") as f:
            f.write(str(period_ns))

    def set_duty(self, duty_ns: int):
        with open(f"{self.path}/duty_cycle", "w") as f:
            f.write(str(duty_ns))

    def shutdown(self):
        self.enable(False)
        # Optional: unexport
        try:
            with open(f"{self.base}/unexport", "w") as f:
                f.write(str(self.channel))
        except:
            pass

class Servo:
    """
    Continuous Servo Control for Raspberry Pi 5 using hardware PWM.
    GPIO12 = PWM0 channel 0  (default recommended)
    """

    def __init__(self, pin: int,
        min_us:  int = 1000,   # full reverse
        max_us:  int = 2000,   # full forward
        stop_us: int = 1500    # neutral/stop
    ):
        if pin != 12 and pin != 13:
            raise ValueError("Servo must use GPIO12 or GPIO13 on Raspberry Pi 5 (hardware PWM).")

        # Map GPIO to correct PWM channel
        # GPIO12 → pwmchip0/pwm0
        # GPIO13 → pwmchip0/pwm1
        channel = 0 if pin == 12 else 1

        self.pwm = HardwarePWM(chip=0, channel=channel)

        # PWM frequency for servos: 50 Hz → 20 ms → 20,000,000 ns
        self.period_ns = 20_000_000
        self.pwm.set_period(self.period_ns)

        self.min_us = min_us
        self.max_us = max_us
        self.stop_us = stop_us

        # Start with servo stopped
        self.stop()
        self.pwm.enable(True)

    def pulse(self, width_us: int):
        width_ns = width_us * 1000
        self.pwm.set_duty(width_ns)

    def stop(self):
        self.pulse(self.stop_us)

    def forward(self, speed: float):
        speed = max(0.0, min(1.0, speed))
        width = self.stop_us + speed * (self.max_us - self.stop_us)
        self.pulse(int(width))

    def reverse(self, speed: float):
        speed = max(0.0, min(1.0, speed))
        width = self.stop_us - speed * (self.stop_us - self.min_us)
        self.pulse(int(width))

    def shutdown(self):
        self.pwm.shutdown()
