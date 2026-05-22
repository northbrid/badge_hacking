#/bin/bash
ls /dev/ | grep cu.usbserial | xargs -I {} esptool -p /dev/{} chip-id
ls /dev/ | grep cu.usbserial | xargs -I {} esptool -p /dev/{} flash-id
