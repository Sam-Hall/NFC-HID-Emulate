#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# exceptions.py - Output exceptions module
#


class UnsupportedPlatformException(Exception):
    """Raised when a supported platform was not detected"""
    def __init__(self, *args):
        Exception.__init__(self, "Keyboard emulation is not supported on this platform", *args)
