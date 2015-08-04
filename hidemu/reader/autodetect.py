#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# autodetect.py - Reader detection module
#
# Reader detection (allows for future expansion to support other models)
#

"""Auto Detect Reader Model

Attempt to detect the reader and select the correct class from the (not so extensive) list of supported readers.

"""

import exceptions

from smartcard.System import readers
from smartcard.pcsc import PCSCExceptions


def reader_exists(reader_prefix):
    """Returns boolean based on the existence of our reader

    The just happens to be the first place the app falls over if pcsc isn't available,
    beware the anecdotal attempt at cross platform exception handling."""
    try:
        for r in readers():
            if reader_prefix in str(r) and str(r).index(reader_prefix) == 0:
                return True
        return False
    except TypeError:  # Occurs when SCardSvr is not running on Windows
        raise exceptions.PyScardFailure
    except PCSCExceptions.ListReadersException:  # When pcscd is not running
        raise exceptions.PyScardFailure


# Search for readers by name and import the appropriate backend module
# SUPPORT FOR ADDITIONAL READERS MAY BE ADDED IN VIA THIS BLOCK HERE!
if reader_exists("ACS ACR122"):
    import acr122 as reader
# elif usb_device_exists("MY READER"):
#     import my_reader as reader
else:
    raise exceptions.ReaderNotFoundException


class Reader(reader.Reader):
    """NFC Reader class"""
    pass
