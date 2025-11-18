import lgpio
import time

CHIP = 0          # gpiochip0
PIN = 12          # BCM 12 (PWM1_0)

PWM_FREQUENCY = 500     # Hz
DUTY_PERCENT = 50       # 50% duty

# Open controller instance
h = lgpio.gpiochip_open(CHIP)

print(f"Starting PWM on GPIO{PIN} @ {PWM_FREQUENCY} Hz, {DUTY_PERCENT}% duty")

# Start PWM
lgpio.tx_pwm(h, PIN, PWM_FREQUENCY, DUTY_PERCENT)
print("50%")
time.sleep(5)

# Stop PWM
lgpio.tx_pwm(h, PIN, PWM_FREQUENCY, 0)
time.sleep(5)

# Close the connection
lgpio.gpiochip_close(h)
print("PWM stopped.")
