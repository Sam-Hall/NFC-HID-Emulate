#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# base.py - reader-agnostic stuff

"""ReaderBase abstract class defined here"""

from smartcard.util import toHexString


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

        # Card feature support matrix as determined by ATR
        # The key purpose is to enable specific features only on recognised card types
        # [description, type code, sub-type code, sector auth, read]
        self.atr_support_matrix = {
            "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 01 00 00 00 00 6A":
            ["Mifare Classic 1k", "MFC", "1K", True, True],

            "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 02 00 00 00 00 69":
            ["Mifare Classic 4k", "MFC", "4K", True, True],

            "3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00 68":
            ["Mifare Ultralight", "MFU", "", True, True],

            "3B 87 80 01 C1 05 2F 2F 01 BC D6 A9":
            ["Mifare Plus", "MFP", "", False, False],
        }
        self.default_support = ["Unknown", "UKN", "", False, False]

    def process_atr(self, atr):
        self.card_ATR = atr
        try:
            support = self.atr_support_matrix[toHexString(atr)]
        except KeyError:
            support = self.default_support
        self.card_description, self.card_type, self.card_subtype, self.card_authable, self.card_readable = support

    def read_block(self, connection, block, length, key_a_num=None, key_b_num=None):
        return []

    @staticmethod
    def load_keys(connection, key_0=None, key_1=None):
        pass

    @staticmethod
    def get_serial_number(connection):
        return None
