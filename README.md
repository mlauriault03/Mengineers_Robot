# Mengineers Robot

## Instructions

Run the following commands in a terminal on the Raspberry Pi:
```
cd Mengineers_Robot/
sudo docker build --platform linux/arm64 -t codrone-test .
sudo docker run -it --rm --device=/dev/ttyACM0:/dev/ttyACM0 --privileged codrone-test
```