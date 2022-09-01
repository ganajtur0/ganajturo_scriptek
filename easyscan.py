#!/bin/python3
import os
import re
import subprocess
import curselect

print("Checking for input peripherals...")

stream = os.popen("scanimage -L")
lines = stream.read()

m = re.findall(r'`(.*)\' is a (.*)', lines, re.MULTILINE)

device_names = []

def dispatch(t):
    device_names.append(t[0])
    return t[1]

devices = [ dispatch(t) for t in m ]

device_menu = curselect.CurSelect(devices, "Devices: ")
device = device_names[device_menu.activate()]
print("Using: ",device)

scan_mode_menu = curselect.CurSelect(["Color", "Gray", "Lineart"], "Scan mode:", ret_type="value")
scan_mode = scan_mode_menu.activate()
print("Scan mode: ", scan_mode)

resolution_menu = curselect.CurSelect(["75", "150", "300", "600"], "Resolution (in dpi):", ret_type="value")
resolution = resolution_menu.activate()
print("Resolution: ", resolution)

fformat_menu = curselect.CurSelect(["pnm", "tiff", "png", "jpeg", "pdf"], "File format:", ret_type="value")
fformat = fformat_menu.activate()
print("File format:", fformat)

output_file = os.path.expanduser(input("Name of output file: "))

command = ["scanimage", "-p", "-d", device, "--mode", scan_mode, "--resolution", resolution, "--format", fformat, "-o", output_file]

print("Executing {}".format((' ').join(command)))

subprocess.run(command)
