# Loading Wifi Drivers

if false; then
    killall wpa_supplicant
    killall wpa_supplicant_nl80211

    insmod /oem/usr/ko/lib80211.ko
    insmod /oem/usr/ko/lib80211_crypt_ccmp.ko
    insmod /oem/usr/ko/lib80211_crypt_wep.ko
    insmod /oem/usr/ko/r8188eu.ko
fi

# Loading Serial Drivers
insmod /oem/usr/ko/cdc-acm.ko

