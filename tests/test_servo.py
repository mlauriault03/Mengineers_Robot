# Servo test
# 11/20/25


# PUBLIC LIBRARIES
import lgpio
import time


# PRIVATE LIBRARIES
from servo import Servo


# PARAMETERS
CHIP = 0                # gpiochip0
PIN = 12                # BCM GPIO 12
PULSE_FORWARD = 2000    # [ms] full speed forward
PULSE_NEUTRAL = 1500    # [ms] stop
PULSE_REVERSE = 1000    # [ms] full speed reverse
PERIOD = 20000          # [us] 20ms 50 Hz


def send_servo_pulse(chip, pin, pulse_width_us):
    # High for pulse_width_us, low for the rest of the 20ms period
    lgpio.tx_pulse(chip, pin, pulse_width_us, PERIOD - pulse_width_us)


def test1():
    """Test servo by cycling through forward, stop, reverse."""
    print("Starting servo test. Press Ctrl+C to stop.")
    # Open chip
    h = lgpio.gpiochip_open(CHIP)
    lgpio.gpio_claim_output(h, PIN)

    try:
        while True:
            print("Forward...")
            for _ in range(100):   # 100 pulses → 2 seconds
                send_servo_pulse(h, PIN, PULSE_FORWARD)
                time.sleep(0.02)

            print("Stop...")
            for _ in range(50):    # 50 pulses → 1 second
                send_servo_pulse(h, PIN, PULSE_NEUTRAL)
                time.sleep(0.02)

            print("Reverse...")
            for _ in range(100):
                send_servo_pulse(h, PIN, PULSE_REVERSE)
                time.sleep(0.02)

    except KeyboardInterrupt:
        pass

    finally:
        # Send a stop pulse before exiting
        for _ in range(20):
            send_servo_pulse(h, PIN, PULSE_NEUTRAL)
            time.sleep(0.02)

        lgpio.gpiochip_close(h)
        print("Servo test finished.")


def test2():
    """Test custom Servo library by cycling through forward, stop, reverse."""
    print("Starting Servo class test. Press Ctrl+C to stop.")
    servo = Servo(PIN, CHIP, PULSE_REVERSE, PULSE_FORWARD, PULSE_NEUTRAL)

    try:
        while True:
            print("Forward...")
            servo.set_speed(1.0)
            time.sleep(2.0)

            print("Stop...")
            servo.set_speed(0.0)
            time.sleep(1.0)

            print("Reverse...")
            servo.set_speed(-1.0)
            time.sleep(2.0)

    except KeyboardInterrupt:
        pass

    finally:
        servo.stop()
        servo.shutdown()
        print("Servo class test finished.")


# If this file is run as a script
if __name__ == "__main__":
    test2()