R.A.T.9 Configurator
====================
(Name subject to change)

This is a simple utility written in python to allow you managing your Saitek
R.A.T 9 mouse (by Madcatz) under Linux or any other operating system supported
by the toolkits. The USB protocol has been completely reverse-engineered.

LICENSE
-------
This is free software, distributed under the GPL v.3. If you want to discuss
a release under another license, ask the author (see below).

AUTHORS
-------
Mayeul Cantan <mayeul.cantan "at" gmail.com>

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
sudo ./configurator.py
```

REQUIEREMENTS
-------------
As it is written in python, you will need python3, and PyQt5.

TODO
----
* Support of multiple peripherals (unlikely to happen, but you can never
  be too sure)
* Comment the code... Well, it doesn't need much, but it needs it.
* Better error handling (present a message if the mouse is not found, etc...)

FEATURE LIST
------------
Any feature present in the windows driver should be in. If not, let me know.
The only exception to this is macro support (together with the precision
button) : Those features are part of an other module in the windows driver,
and it is the way it sould be implemented.
