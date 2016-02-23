ratctl
======

This is a simple utility written in python to allow you managing your R.A.T
mouse under Linux or any other operating system supported by the toolkits. 
The USB protocol has been completely reverse-engineered.
Be sure to check out the 
[Wiki](https://github.com/MayeulC/Saitek/wiki/R.A.T-9-USB-Documentation) 
for tips, and raw information.

LICENSE
-------
This is free software, distributed under the GPL v.3. If you want to discuss
a release under another license, please open an issue on Github

NOTES
-----
As usual with this kind of software :
This software is provided "AS-IS", without any guarantees. It should not do
any harm to your system, but if it does, the author, github, etc... cannot
be held responsible. Use at your own risk. You have been warned.

Keep in mind I am not really used to python (I am mainly a C programmer),
so any contribution will be welcomed, provided it is constructive.
Python was used to ease the development, but a C implementation would be
great too.

USAGE
-----
easiest way :
```Shell
sudo ./ratctl.py
```

REQUIEREMENTS
-------------
As it is written in python, you will need python3, and PyQt5.
Libusb1-python is required too.
It should work on any machine supporting these three, but the code has been
written with little endian (x86) in mind, so this could require some adjustments.

You could experience some difficulties in installing the libusb1 library for python. The 
preferred method is trough ```pip```. Just keep in mind that the tool is using python3, so 
you may have to use the ```pip3``` or ```pip3.x``` binary. The command should be something 
like
```Shell
sudo pip install libusb1
```
TODO
----
* Support of multiple peripherals (it is unlikely anyone will ever use this, but you 
can never be too sure)
* Comment the code... Well, it doesn't need much, but it needs it.
* Better error handling (present a message if the mouse is not found, etc...)
* Support other mices, with their different features

CONTRIBUTING
------------
Here's how you can help : 
* Check if it works with your mouse (R.A.T 3 and 5 mice as well)
* If it doesn't, please open an issue with the lsusb output, and general information about your mouse
* You can clone the git repository and start hacking with the code. Pull requests are most welcome.

FEATURE LIST
------------
Any feature present in the windows driver should be in. If not, let me know.
The only exception to this is macro support (together with the precision
button) : Those features are part of an other module in the windows driver,
and it is the way it sould be implemented.

The exhaustive list is : 
* Query and display battery level
* Change, and display current DPI mode
* Change per-axis, per-mode DPI
* Reset default configuration
