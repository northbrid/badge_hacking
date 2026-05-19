# Insert your Wifi credentials here
cat <<EOF | tee /etc/wpa_supplicant.conf
ctrl_interface=/var/run/wpa_supplicant
ap_scan=1
update_config=1

network={
    ssid="YOUR_SSID"
    psk="YOUR_PASSWORD"
}
EOF

## WIFI CONFIGURATION. DO NOT EDIT.

# Stop existing processes
killall wpa_supplicant
killall wpa_supplicant_nl80211

# Bring up interface
ifconfig wlan0 up
# iwlist wlan0 scan
# mkdir /var/run/wpa_supplicant -p

# Start wpa_supplicant
wpa_supplicant -B -i wlan0 -D wext -c /etc/wpa_supplicant.conf

# Retrieve IP address
udhcpc -i wlan0
sleep 3

ifconfig -a wlan0
echo "== END OF WIFI SETUP =="
