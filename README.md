# ACR122 HID Emulate
Human Interface Device emulator for ACR122 NFC readers. The niche purpose being to provide similar functionality to that of a standard USB HID Magnetic Stripe Reader (MSR). Defaults to simply returning the chip serial number in a similar format to that of a MSR.

Testing performed only on the ACR122U model, but other USB models should work with some minor modifications to the reader package.

## Platforms
Developed with Python versions 2.7.6 and 2.7.10

### Windows
Tested on Win7 64bit

Maintain same architecture as OS (reader drivers and python stuff)

Requires:

* pyscard

### Linux
Tested on Ubuntu 14.04 and 14.10

Requires (OS Packages):

* ACS Unified Linux drivers
* pcscd
* swig
* libpcsclite-dev
* python-xlib
* pyscard (build latest from source)

### OSX - Unsupported
Unsuccessfully tested on OSX 10.10

Unable to build as yet, problems with both the output and reader packages. Should work in theory.

Requires:

* pyobjc
* swig
* pyscard

