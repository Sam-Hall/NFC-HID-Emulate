#!/usr/bin/env python
# Copyright (c) 2017 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# omnikey5x21cl.py - Controls the Omnikey 5x21 CL reader

"""Omnikey 5x21 CL reader module

All Omnikey 5x21 CL specific code goes here.

"""

import logging
import exceptions
from base import ReaderBase
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.util import toHexString, toBytes

# Omnikey Documented Commands including a short description for error handling
# Typical command format: [class, ins, p1, p2, lc] + data byte list
PICC_CMD_GET_DATA   = ["Fetch UID",   [0xFF, 0xCA, 0x00, 0x00, 0x00]]
PICC_CMD_LOAD_KEY_0 = ["Load Key 0",  [0xFF, 0x82, 0x20, 0x00, 0x06]]  # + key byte list
PICC_CMD_LOAD_KEY_1 = ["Load Key 1",  [0xFF, 0x82, 0x20, 0x01, 0x06]]  # + key byte list
PICC_CMD_MFC_AUTH   = ["Sector Auth", [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00]]  # + [block num, key type A/B, key num]
PICC_CMD_READ_BLOCK = ["Read Block",  [0xFF, 0xB0, 0x00]]  # + [block num, length]



class Reader(ReaderBase):
    """Omnikey 5x21 CL reader class

    Support for basic reading operations.
    """

    def __init__(self):
        ReaderBase.__init__(self)
        self.prefix = "OMNIKEY CardMan 5x21-CL"
        self.reader = Reader._find_reader(self.prefix)
        self.logger = logging.getLogger('hidemu')

        # Flag to ensure keys are loaded upon next connection.
        # These values are reset once keys are loaded.
        self.key_load_pending = False
        self.key_0_byte_list = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.key_1_byte_list = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    def connect(self, timeout=1, new_card_only=True):
        """Returns a connection if possible, otherwise returns None"""
        card_request = CardRequest(readers=[self.reader], timeout=timeout, newcardonly=new_card_only)
        card_service = card_request.waitforcard()
        try:
            # Establish reader-centric connection
            connection = self.reader.createConnection()
            connection.connect()
            self.process_atr(connection.getATR())

            # Load keys if need be
            self.card_authentication = None
            if self.key_load_pending and self.card_authable:
                self._load_keys(connection)

            return connection
        except (CardConnectionException, NoCardException):
            return None

    def read_block(self, connection, block, length, key_a_num=None, key_b_num=None):
        """Either key A or B must be specified for Mifare Classic cards"""
        if not self.card_readable: raise exceptions.NotSupportedException("Read From Card")
        if self.card_authable:
            valid_num = [0x00, 0x01]
            assert key_a_num in valid_num or key_b_num in valid_num
            sector = block >> 2
            if sector >= 32: sector = ((sector-32) >> 2) + 32  # 4K MFC cards have 8 sectors of 16 blocks at the end
            if self.card_authentication != [sector, key_a_num, key_b_num]:
                Reader._auth_mfc(connection, block, key_a_num, key_b_num)
                self.card_authentication = [sector, key_a_num, key_b_num]
        return Reader._read_block(connection, block, length)

    def set_keys(self, key_0=None, key_1=None):
        """Specify reader keys 0 and 1 as 12 character hex strings (not to be confused with sector keys A and B)

        These keys will be used to access blocks, at that time either key 1 or 2 can be used as key A and/or B.

        Omitting a key will revert it to the default FF key"""
        if key_0 is None: key_0 = "FFFFFFFFFFFF"
        if key_1 is None: key_1 = "FFFFFFFFFFFF"
        assert len(key_0) == 12 and len(key_1) == 12
        assert int(key_0, 16) and int(key_1, 16)  # throws ValueError if not a hex string

        # Set a flag to load the keys as soon as the next card arrives
        self.key_0_byte_list = toBytes(key_0)
        self.key_1_byte_list = toBytes(key_1)
        self.key_load_pending = True

    def _load_keys(self, connection):
        """Load keys into the reader"""
        assert len(self.key_0_byte_list) == 6 and len(self.key_1_byte_list) == 6
        Reader._transmit(connection, PICC_CMD_LOAD_KEY_0, self.key_0_byte_list)
        Reader._transmit(connection, PICC_CMD_LOAD_KEY_1, self.key_1_byte_list)

        for i in range(0, 6):  # Wipe the stored key
            self.key_0_byte_list[i] = 0xFF
            self.key_1_byte_list[i] = 0xFF
        self.key_load_pending = False

    @staticmethod
    def get_serial_number(connection):
        """Returns card serial number in bytes"""
        return Reader._transmit(connection, PICC_CMD_GET_DATA)

    @staticmethod
    def _transmit(connection, command, command_vars=None):
        """Returns: data as a byte list"""
        if command_vars is None: command_vars = []
        command_desc = command[0]
        full_command = command[1] + command_vars
        sw = [0, 0]
        try:
            data, sw[0], sw[1] = connection.transmit(full_command)
        except(AttributeError, IndexError):
            # Connection lost
            raise exceptions.ConnectionLostException
        response_code = toHexString(sw)
        if response_code == "64 00":  # card execution error
            raise exceptions.FailedException(command_desc)
        elif response_code == "67 00":  # wrong length
            raise exceptions.NotSupportedException(command_desc)
        elif response_code == "68 00":  # invalid class (CLA) byte
            raise exceptions.NotSupportedException(command_desc)
        elif response_code == "69 81":  # Command incompatible.
            raise exceptions.FailedException(command_desc)
        elif response_code == "69 82":  # Security status not satisfied.
            raise exceptions.FailedException(command_desc)
        elif response_code == "69 86":  # Command not allowed.
            raise exceptions.FailedException(command_desc)
        elif response_code == "6A 81":  # invalid instruction (INS) byte
            raise exceptions.NotSupportedException(command_desc)
        elif response_code == "6A 82":  # File not found / Addressed block or byte does not exist.
            raise exceptions.FailedException(command_desc)
        elif response_code.startswith("6C"):  # wrong length
            raise exceptions.NotSupportedException(command_desc)
        elif response_code != "90 00":
            raise exceptions.UnexpectedErrorCodeException(response_code, command_desc, sw[0], sw[1])
        return data

    @staticmethod
    def _read_block(connection, block, length):
        assert 0x00 <= block <= 0xff
        assert 0x00 <= length <= 0xff

        data = Reader._transmit(connection, PICC_CMD_READ_BLOCK, [block, length])
        return data

    @staticmethod
    def _auth_mfc(connection, block, key_a=None, key_b=None):
        """Either key A or B must be specified"""
        reader_keys = [0x00, 0x01]
        assert key_a in reader_keys or key_b in reader_keys
        assert 0x00 <= block <= 0xff

        if key_a is not None:
            Reader._transmit(connection, PICC_CMD_MFC_AUTH, [block, 0x60, key_a])
        if key_b is not None:
            Reader._transmit(connection, PICC_CMD_MFC_AUTH, [block, 0x61, key_b])