# ACR122 HID Emulate
Human Interface Device emulator for ACR122 NFC readers. The niche purpose being to provide similar functionality to that of a standard USB HID Magnetic Stripe Reader (MSR). Defaults to simply returning the chip serial number in a similar format to that of a MSR.

Testing performed only on the ACR122U model, but other USB models should work with some minor modifications to the reader package.

## Platforms
Developed with Python versions 2.7.6 and 2.7.10

### Windows
Tested on Win7 64bit

Maintain same architecture as OS (reader drivers and python stuff)

Requires:

* pyscard 1.7
* No drivers required

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
Unsuccessfully tested on OSX 10.10

Reader working, output package still out of order (just crashes Python). One clue from the internet is that perhaps Python 2.6 would work better for the pyobjc Quartz requirement.

Another hurdle I'm still yet to hit is that OSX 10.10 requires a security exception to enable the accessibility features required to emulate keystrokes. How to go about that during development I have no idea. I don't intend to pursue OSX support any further, but if anyone gets it working feel free to share your secrets in the issues register.

Requires:

* ACS Unified Installer OSX drivers
* pyobjc
* swig (to build pyscard from source)
* pyscard (build latest from source)
