# Preface 

For sniffing, I need to compile and install this tool: https://github.com/homewsn/whsniff

# Running the sniffer

This will print the captured packets in Wireshark's PCAP format to the STDOUT,  
so I need to run it with redirecting the output: `whsniff -c 11 > capture.pcap`  
The channel parameter is mandatory, one dongle can sniff in one channel. 

# Running multiple sniffers

If I want to listen on multiple channels in the same time, I need multiple dongles. 
In my case, I have four, and I can plug in all of them with an USB hub. 
But, the whsniff software does not let you specify the device you want to use. 
It will just walk through the USB devices and select the first compatible device. 

As a workaround, I can do the following sequence of steps:
* Plug in the first dongle
* Start the whsniff command for channel 11 in the background
* Plug in the second dongle
* Start the whnsiff command for channel 12 in the background
* Plug in the third dongle
* Start the whsniff command for channel 13 in the background
* ... and so on.

The new instances will see ports that are already in use, and will try to free them up.
These attempts will fail with __com.apple.vm.device-access__ entitlement error. 
You will see as many of these errors, as many whsniff commands are already running. 
But finally it will work. 

# Hopping

As we can only listen on one channel at a time, I created a script that implements hopping. 
It is not complicated, but we need to write the PCAP header once and then skip it when appending. 
I also implemented a good console UI that displays the count of packages in the different channels. 

# Hopping with multiple sniffers

It should be possibe to listen on N channels in the same time, and then jump to the next N channels. 
For example: listening on 11-12-13-14, and then jumping to 15-16-17-18, reducing the number of steps. 
This is a good thing, as it will significantly reduce the time when we do not listen on a channel. 
But, because of the trick we need to use for running multiple sniffers, this is not possible yet. 


