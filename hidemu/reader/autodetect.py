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

from smartcard.System import readers

COMPATIBLE_READER_NOT_DETECTED = "Reader could not be detected"


def reader_exists(reader_prefix):
    for r in readers():
        if reader_prefix in str(r) and str(r).index(reader_prefix) == 0:
            return 1
    return 0


# Search for readers by name and import the appropriate backend module
# SUPPORT FOR ADDITIONAL READERS MAY BE ADDED IN VIA THIS BLOCK HERE!
if reader_exists("ACS ACR122"):
    import acr122 as reader
# elif usb_device_exists("MY READER"):
#     import my_reader as reader
else:
    raise Exception(COMPATIBLE_READER_NOT_DETECTED)


class Reader(reader.Reader):
    """NFC Reader class."""
    pass

