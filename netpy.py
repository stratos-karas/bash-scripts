#! /usr/bin/env python

import os
import signal
import sys
import time
import subprocess
import re


# Create a new net log file
os.system("touch .netlog")

# Check the wireless network interface
net_interfaces = str(subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE).communicate()[0])

# Find the system's wlan interface
wlan_interface = re.search("wlan0", net_interfaces)
if wlan_interface == None:
    wlan_interface = re.search("wlp[0-9]s[0-9]", net_interfaces)

# If there is none
if wlan_interface == None:
    print("No wireless network interface dtected")
    sys.exit(0)
# We found a wirless interface
else:
    wlan_interface = str(wlan_interface.group())

# Check if iwconfig is installed
'''
TODO: completely remove this dependency
(maybe root access will be needed)
'''
ret = os.system("iwconfig " + wlan_interface + " > .netlog")
if ret != 0:
    print("You should install iwconfig to your sytsem first")

# Signal Handler
def handler(signal_num, frame):
    # If file pointer not closed
    # do so
    if not fp.closed:
        fp.close()

    # Remove the log file
    os.system("rm .netlog")

    # Clear screen
    os.system("clear")

    # Exit normally the program
    sys.exit(0)

# Define the signal handler for the program
signal.signal(signal.SIGINT, handler)

while 1:
    
    # Open up the .netlog file
    fp = open(".netlog")
    # Read from the file the available info
    line = fp.readline()
    
    # Link, Signal, Noise spanning init
    link_quality_span = None
    signal_level_span = None
    noise_level_span = None
    
    while line:
        if line.startswith("          Link Quality"):
            
            # Fetch all the necessary info if there are any
            re_link_quality = re.search("Link Quality", line)
            re_signal_level = re.search("Signal level", line)
            re_noise_level  = re.search("Noise level", line)

            if re_link_quality != None:
                link_quality_span = re_link_quality.span()

            if re_signal_level != None:
                signal_level_span = re_signal_level.span()

            if re_noise_level != None:
                noise_level_span = re_noise_level.span()

            break

        line = fp.readline()
   
    # Output string
    if link_quality_span != None and signal_level_span != None:
        link_quality_out = line[link_quality_span[0]:signal_level_span[0]-1]
    elif link_quality_span != None and noise_level_span != None:
        link_quality_out = line[link_quality_span[0]:noise_level_span[0]-1]
    elif link_quality_span != None:
        link_quality_out = line[link_quality_span[0]:]
    else:
        link_quality_out = ""

    if signal_level_span != None and noise_level_span != None:
        signal_level_out = line[signal_level_span[0]:noise_level_span[0]-1]
    elif signal_level_span != None:
        signal_level_out = line[signal_level_span[0]:]
    else:
        signal_level_out = ""

    if noise_level_span != None:
        noise_level_out = line[noise_level_span[0]:]
    else:
        noise_level_out = ""

    # Metaprocessing of newline escape character
    link_quality_out = link_quality_out.replace("\n", "")
    signal_level_out = signal_level_out.replace("\n", "")
    noise_level_out = noise_level_out.replace("\n", "")
    
    # Create dynamic string based on terminal columns number
    # Terminal columns
    cols = int(subprocess.Popen(['tput', 'cols'], stdout=subprocess.PIPE).communicate()[0])
    out = "\033[47m \033[30m" + link_quality_out + "\033[0m" +\
            "\n\033[3;0H\r" + "\033[44m " + signal_level_out + "\033[0m" +\
            "\n\033[4;0H\r" + "\033[41m " + noise_level_out + "\033[0m\033[2;0H"
    
    if len(out) > cols:
        # Flush the color so that the terminal
        # will return to its default setting
        out = out[:cols] + "\033[0m"
    
    sys.stdout.write("\r" + out)
    sys.stdout.flush()
    # Close file
    fp.close()

    # Write new wireless info to the file
    os.system("iwconfig " + wlan_interface + " > .netlog")
    
    # Let the program sleep for half a second
    time.sleep(0.5)
