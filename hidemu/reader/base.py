#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# base.py - reader-agnostic stuff

"""ReaderBase abstract class defined here"""

from smartcard.util import toHexString

# Card feature support matrix as determined by ATR
# The key purpose is to enable specific features only on recognised card types
# [description, type code, sub-type code, sector auth, read]
ATR_SUPPORT_MATRIX = {
    "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A":
    ["Mifare Classic 1k", "MFC", "1K", True, True],
    "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 02 00 00 00 00 69":
    ["Mifare Classic 4k", "MFC", "4K", True, True],
    "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00 68":
    ["Mifare Ultralight", "MFU", "", True, True],
    "3B 87 80 01 C1 05 2F 2F 01 BC D6 A9":
    ["Mifare Plus", "MFP", "", False, False],
}
DEFAULT_SUPPORT = ["Unknown", "UKN", "", False, False]


class ReaderBase:
    """Reader base class"""

    def __init__(self):
        self.reader = None
        # TODO: Seems like a Card class is in order
        self.card_ATR = None
        self.card_authentication = None
        self.card_description = None
        self.card_type = None
        self.card_subtype = None
        self.card_authable = False
        self.card_readable = False

    def process_atr(self, atr):
        """Find details of supported features from ATR_SUPPORT_MATRIX"""
        self.card_ATR = atr
        try:
            support = ATR_SUPPORT_MATRIX[toHexString(atr)]
        except KeyError:
            support = DEFAULT_SUPPORT
        self.card_description, self.card_type, self.card_subtype, self.card_authable, self.card_readable = support

    def connect(self, timeout=1, new_card_only=True):
        """Returns a connection if possible, otherwise returns None"""
        return None

    def read_block(self, connection, block, length, key_a_num=None, key_b_num=None):
        return []

    def error_signal(self, duration=6):
        """If possible, blink or bleep at the user (for about 6 seconds by default)"""
        pass

    @staticmethod
    def load_keys(connection, key_0=None, key_1=None):
        """Load one or two keys into the reader"""
        pass

    @staticmethod
    def get_serial_number(connection):
        """Return the card serial number as a list of bytes"""
        return None
