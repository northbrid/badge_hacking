echo "=== SD CARD ==="

mkdir -p /mnt/sdcard
mount /dev/sda1 /mnt/sdcard
# mount /dev/disk/by-id/usb-MXT-USB_Storage_Device_150101v01-0:0-part1 /mnt/sdcard/

mount | grep /mnt/sdcard
ls -la /dev/sd*
