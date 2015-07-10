#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# exceptions.py - Reader exceptions module
#


class ReaderNotFoundException(Exception):
    """Reader not attached or no longer available"""
    def __init__(self, *args):
        Exception.__init__(self, "Reader not found", *args)


class CardNotFoundException(Exception):
    """No card is currently on the device"""
    def __init__(self, *args):
        Exception.__init__(self, "Card not found", *args)


class CSNFailedException(Exception):
    """Failed to fetch serial number"""
    def __init__(self, *args):
        Exception.__init__(self, "Failed to fetch serial number", *args)


class CSNNotSupportedException(Exception):
    """Serial number fetch unsupported (check card type)"""
    def __init__(self, *args):
        Exception.__init__(self, "Serial number fetch unsupported", *args)


class CSNUnexpectedException(Exception):
    """Unexpected error while fetching serial number"""
    def __init__(self, *args):
        Exception.__init__(self, "Unexpected error while fetching serial number", *args)
