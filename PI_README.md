# Raspberry Pi Documentation

## Security Info 

Keyring: admin 

## Setup 

1. Plug SD card into your computer using an SD card adapter 
2. Download Raspberry Pi Imager here and install it on your computer 
3. Open the Raspberry PI Imager 
4. Choose the following options: 
    * Raspberry PI Device: Raspberry Pi 5 
    * Operating System: Raspberry Pi OS (64-bit) 
    * Storage: (select the SD card  - it should be the only option anyway) 
5. Click “Next” 
6. When it prompts you about customizations, click “Edit” and set the following: 
    * Hostname: mengineers 
    * Username: admin 
    * Password: password 
7. Click “Yes” when it asks you if you want to use the customizations 
8. When the imager finishes, eject the SD card from your computer before unplugging it and then insert it into the Raspberry Pi 
9. Power on the Raspberry Pi 
10. Connect it to the BJU-Campus wifi using your BJU credentials and putting “bju.edu” in the “Domain” field 
11. Sign in to the BJU-Campus network in the browser as well 
12. Click the raspberry button at the top left of the screen and navigate to Preferences > Control Centre 
13. Click “Localisation” in the left pane of the Control Centre window and set the options for each of the following buttons: 
    * Set Locale… 
        * Language: en (English) 
        * Country: US (United States) 
        * Character Set: UTF-8 
    * Set Timezone… 
        * Area: America 
        * Location: New York 
    * Set Keyboard… 
        * Model: Generic 105-key PC 
        * Layout: English (US) 
        * Variant: English (US) 
    * Set Wifi Country… 
        * Country: US United States 
14. Click the terminal button at the top left of the screen and enter the following commands: 
```
sudo apt update 
sudo apt upgrade -y 
cd /home/admin 
git clone https://github.com/mlauriault03/Mengineers_Robot 
cd Mengineers_Robot 
git pull 
```

## Raspberry Pi Connect 

### Initial Setup 

1. Run the following commands on the Raspberry Pi: 
```
sudo apt update 
sudo apt install --only-upgrade rpi-connect 
rpi-connect on 
rpi-connect signin 
```
2. Note: if you see an error/warning message that says “Verifying signature: Not live until ...” when running `sudo apt update` then the system time clock is not syncrhonized. To fix this, run the following command in the terminal but adjust the string with the actual date and time:  
```
sudo date -s "YYYY-MM-DD hh:mm:ss" 
```

### Remote Connect 

1. Go to https://connect.raspberrypi.com/devices/f63312dc-ce9e-443c-8b34-96ee576b010e on your computer  
    * Note: if you see Screen sharing: inactive, Remote shell: inactive, and an up-arrow next to the Version, follow the “Initial Setup” instructions above 
2. Click “Connect via” in the top right corner and select one of the following: 
    * “Screen sharing” to open a window with the Raspberry Pi’s screen allowing you to control it as if you’re using it 
    * “Remote shell” if you simply need to run terminal commands on the Raspberry Pi 