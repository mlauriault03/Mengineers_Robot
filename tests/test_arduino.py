import serial
import time

# Adjust port if different
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino reset

commands = ["LED_ON", "LED_OFF"]

for cmd in commands:
    ser.write((cmd + '\n').encode())
    print(f"Sent: {cmd}")
    time.sleep(1)
    while ser.in_waiting > 0:
        print("Arduino:", ser.readline().decode().strip())

ser.close()

