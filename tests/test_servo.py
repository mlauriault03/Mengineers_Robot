# Continous Servo Motor Test
# 11/3/25

import time
import RPi.GPIO as GPIO

# Pin settings
SERVO_PIN = 18   # use GPIO18 (physical pin 12) as hardware PWM
FREQUENCY = 50   # typical servo signal frequency in Hz

# Duty cycle range for your servo
# These values depend on the servo: adjust as needed
MIN_DUTY = 2.5   # e.g., corresponds ~0°
MAX_DUTY = 12.5  # e.g., corresponds ~180°
CENTER_DUTY = (MIN_DUTY + MAX_DUTY)/2

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, FREQUENCY)
    pwm.start(0)
    return pwm

def sweep_servo(pwm, delay=0.02):
    # sweep from MIN to MAX
    print("Sweeping from MIN to MAX")
    for duty in [MIN_DUTY + (MAX_DUTY-MIN_DUTY)*i/100.0 for i in range(101)]:
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay)
    # sweep back
    print("Sweeping from MAX back to MIN")
    for duty in [MAX_DUTY - (MAX_DUTY-MIN_DUTY)*i/100.0 for i in range(101)]:
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay)
    # center
    print("Centering servo")
    pwm.ChangeDutyCycle(CENTER_DUTY)
    time.sleep(1)

def cleanup(pwm):
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        pwm = setup()
        sweep_servo(pwm)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        cleanup(pwm)
        print("Done")