#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# autodetect.py - Reader detection module
#
# Reader detection (allowing for future expansion to support other models)

"""Auto Detect Reader Model

Attempt to detect the reader and select the correct class from the (not so extensive) list of supported readers.

"""

import usb.core

COMPATIBLE_READER_NOT_DETECTED = "Reader could not be detected"


def usb_device_exists(vendor_id, product_id):
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if device is None:
        return 0
    else:
        return 1


# Check for USB device by ID and import the appropriate backend module
# SUPPORT FOR ADDITIONAL READERS MAY BE ADDED IN VIA THIS BLOCK HERE!
if usb_device_exists(0x072f, 0x2200):
    import acr122 as reader
# elif usb_device_exists(0xNNNN, 0xNNNN):
#     import my_reader as reader
else:
    raise Exception(COMPATIBLE_READER_NOT_DETECTED)


class Reader(reader.Reader):
    """NFC Reader class."""
    pass

