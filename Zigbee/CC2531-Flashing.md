The CC2531 USB Dongle has a debug connector, and can be flashed only through that. 
It normally needs a TI programmer which I don't have, but I can also use an ESP32.

The CC loader firmware for ESP32 is located in here: 
https://github.com/xyzroe/XZG-MT/tree/cc_loader
https://github.com/xyzroe/XZG-MT/blob/main/docs/how-to/cc_loader.md

You can easily flash the ESP32 with this FW using the https://mt.xyzroe.cc/ tool.

The different ESP32 dev boards uses GPIO pins for different purposes.
The firmware supports a few, and the pins used for flashing varies.
You can find the DD, DC, and RESET pins of the different boards here:
https://github.com/xyzroe/XZG-MT/blob/cc_loader/bins/manifest.json 

You can see the DD, DC and RESET pins of rhe CC2531 Dongle in the PNG image.
You can find the ESP32 dev board PINs mentioned in the manifest in the another PNG.
Match them, and connect the 3 wires. 

You don't need to use GND and Vdd, just connect the dongle to the USB port. 
Use USBs of the same PC for the dongle and the ESP32, so you have a common GND!
