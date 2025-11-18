import os
import time

PWMCHIP = "/sys/class/pwm/pwmchip0"
CHANNEL = 0

# Export the channel if needed
if not os.path.exists(f"{PWMCHIP}/pwm{CHANNEL}"):
    with open(f"{PWMCHIP}/export", "w") as f:
        f.write(str(CHANNEL))
    time.sleep(0.1)

# Set 50 Hz period (20 ms)
with open(f"{PWMCHIP}/pwm{CHANNEL}/period", "w") as f:
    f.write("20000000")  # 20 ms

# Enable PWM output
with open(f"{PWMCHIP}/pwm{CHANNEL}/enable", "w") as f:
    f.write("1")

# Sweep duty cycle from 5% to 10%
print("Sweeping PWM duty cycle...")
for duty_us in range(500, 2500, 100):
    duty_ns = duty_us * 1000
    with open(f"{PWMCHIP}/pwm{CHANNEL}/duty_cycle", "w") as f:
        f.write(str(duty_ns))
    print("Pulse:", duty_us, "us")
    time.sleep(0.3)

# Disable PWM
with open(f"{PWMCHIP}/pwm{CHANNEL}/enable", "w") as f:
    f.write("0")

print("Done.")
