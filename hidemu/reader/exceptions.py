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


class ConnectionLostException(Exception):
    """Card connection no longer valid"""
    def __init__(self, *args):
        Exception.__init__(self, "Card connection lost", *args)


class FailedException(Exception):
    """Failed to fetch serial number"""
    def __init__(self, *args):
        Exception.__init__(self, "No information given", *args)


class NotSupportedException(Exception):
    """Function not supported (check card type)"""
    def __init__(self, *args):
        Exception.__init__(self, "Function not supported", *args)


class UnexpectedErrorCodeException(Exception):
    """Unexpected error code"""
    def __init__(self, *args):
        Exception.__init__(self, "Unexpected error", *args)
