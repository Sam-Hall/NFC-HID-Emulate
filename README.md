# NFC HID Emulate
Human Interface Device emulator for NFC readers. The niche purpose being to provide similar functionality to that of a standard USB HID Magnetic Stripe Reader (MSR). Defaults to simply returning the chip serial number in a similar format to that of a MSR.

Testing performed initially on the ACR122U model NFC reader, but other ACR brand USB models should work with some minor modifications to the reader package.

Reader support recently added for SDI011 and Omnikey 5x21 CL (tested specifically with Omnikey 5021 CL model). Only tested these readers on Windows.

Designed to run as a service in the background (or more accurately, a user daemon - since it requires the current user desktop session to function). The ideal time to start the program is on login. To avoid conflicts, the application will only attempt to load once. You may have problems getting it to work after switching users unless the first user logs out completely.

There are some command line args, you can bring up all currently available options with the "-h" switch.

## Platforms
Developed with Python versions 2.7.6 and 2.7.10

### Windows
Tested on Win7 64bit

Maintain same architecture as OS (reader drivers and python stuff)

Requires:

* pyscard 1.7
* No drivers required
* Smart Card service required (should start as soon as the reader installs via Plug and Play)

### Linux
Tested on Ubuntu 14.04 and 14.10

Requires:

* ACS Unified Linux drivers
* pcscd
* libpcsclite-dev
* python-xlib
* swig (to build pyscard from source)
* pyscard (build latest from source)

### OSX - Unsupported
Currently no intention to develop the keyboard emulation features required to make the output package work on OSX. Brief attempts to integrate osxkeyboardcontrol.py from Plover project proved fruitless on OSX 10.10.

Since I have no need for OSX support, this option has been shelved. If you need OSX support, it should be possible to emulate key strokes via the "pyobjc-framework-quartz" package and some security/accessibility settings which need to be applied through System Preferences.

Any OSX specific output modules have been removed (the modules were borrowed pretty much verbatim from Plover project anyway).

Requires:

* ACS Unified Installer OSX drivers
* pyobjc
* swig (to build pyscard from source)
* pyscard (build latest from source)
