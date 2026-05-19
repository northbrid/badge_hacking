#!/bin/sh

# First Boot
if [ ! -f /root/scripts/.first_boot_done ]; then
    echo "== Initializing board for first boot =="
    bash /root/scripts/first_boot.sh
    echo "== Rebooting after first boot script =="
    sleep 1
    reboot
fi

# Normal Boot
echo "== Hello world! =="

# Logo
#ffmpeg -re -i /root/images/csit.png -pix_fmt rgb565le -vf scale=320:240,transpose=2,negate -f fbdev /dev/fb0 > /dev/null;
# python3 /root/scripts/display_png.py /root/images/csit.png &

# Drivers
#bash /root/scripts/drivers.sh || true

# SD Card
bash /root/scripts/sdcard.sh || true

# RGB LEDs
#python3 /root/scripts/rgb.py &

# Wifi
## bash /root/scripts/wifi.sh

# Application
python3 /root/app.py &

