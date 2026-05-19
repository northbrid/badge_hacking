# DCSG1 CSIT Badge

## Bill Of Materials

* RockChip RV1103G1  
  https://rockchip.fr/RV1103%20datasheet%20V1.5.pdf
* WinBond 25N01KVZEIR  
  https://www.marthel.pl/katalog/W25N01KVxxxR_Datasheet_Rev.F_20230418.pdf
* GENESYS GL823K  
  https://w.electrodragon.com/w/images/c/cb/GL823K.pdf
* CoreChip SL2.1A USB2.0 HUB JY0917B25  
  https://www.graylogix.in/wp-content/uploads/2025/07/2409271302_CoreChips-SL2-1A_C192893.pdf
* YF08E / TXS0108E  
  https://cdn.sparkfun.com/assets/1/8/1/e/2/txs0108e.pdf

## Interfaces

* The SD card contains images and videos, which the badge can play.
* The USB1 port enumerates an USB-to-UART interface which runs at baud __115200__

## Software

* The badge runs Linux, and identifies itself as luckfox pico.  
* I can easily find the default root password in internet: `luckfox`
* After logged in, I copied the scripts and uploaded them to the `root` folder.
* I also uploaded 2 different console logs to the `screenlog` folder
  * `screenlog.0` is the normal mode, we can see the Linux kernel booting. 
  * `screenlog.1` is when I keep the __boot__ button pressed when turning on.

