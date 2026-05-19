# Hardware config
cat <<EOF | tee /etc/luckfox.cfg
SPI0_M0_CS_ENABLE=1
SPI0_M0_MODE=1
UART4_M1_STATUS=1
UART3_M1_STATUS=1
FBTFT_ENABLE=1
USB_MODE=host
EOF

sync

# Manually change USB mode
set -- load
source /usr/bin/luckfox-config
luckfox_usb_app host

# Test LCD
dd if=/dev/urandom of=/dev/fb0 bs=$((240*320)) count=2

# Test LEDs
stty -F /dev/ttyS3 2500000 cs7 -parenb -cstopb
python3 -c "print('[[[[[[ZS'*10)" > /dev/ttyS3 # Blue
python3 -c "print('[ZS[[[[['*10)" > /dev/ttyS3 # Green
python3 -c "print('[[[R[[[['*10)" > /dev/ttyS3 # Red

# Program
python3 -c "print('\x00\x66'*320*240)" > /dev/fb0

# Complete first boot
echo "@zst123" > /root/scripts/.first_boot_done

