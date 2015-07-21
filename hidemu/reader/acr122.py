#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# acr122.py - Controls the ACR122 reader

"""ACR122 reader module

All ACR122 specific code goes here.

"""

import exceptions
from smartcard.System import readers
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException, NoCardException
from smartcard.util import toHexString

READER_PREFIX = "ACS ACR122"

# ACR122 API Documented Commands including a short description for error handling
# Typical command format: [class, ins, p1, p2, lc] + data byte list
PICC_CMD_GET_DATA   = ["Fetch UID",   [0xFF, 0xCA, 0x00, 0x00, 0x00]]
PICC_CMD_LOAD_KEY_0 = ["Load Key 0",  [0xFF, 0x82, 0x00, 0x00, 0x06]]  # + key byte list
PICC_CMD_LOAD_KEY_1 = ["Load Key 1",  [0xFF, 0x82, 0x00, 0x01, 0x06]]  # + key byte list
PICC_CMD_MFC_AUTH   = ["Sector Auth", [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00]]  # + [block num, key type A/B, key num]
PICC_CMD_READ_BLOCK = ["Read Block",  [0xFF, 0xB0, 0x00]]  # + [block num, length]

# Example Pseudo-APDU read command (may need similar such commands for Mifare Plus)
PICC_CMD_READ_BLOCK0_DIRECT = ["Read Block Direct", [0xFF, 0x00, 0x00, 0x00, 0x05, 0xD4, 0x40, 0x01, 0x30, 0x00]]

DEBUG = False


class Reader:
    """ACR122 reader class

    Built for ACR122U but may support similar USB models. This class will only ever support basic reading operations.
    Assumes reader will remain connected for the duration of program execution."""

    def __init__(self):
        self.reader = Reader._find_myself()
        # Current card...
        self.card_ATR = None
        self.card_authentication = None
        pass

    def connect(self, timeout=1, new_card_only=True):
        """Returns a connection if possible, otherwise returns None"""
        card_request = CardRequest(readers=[self.reader], timeout=timeout, newcardonly=new_card_only)
        card_service = card_request.waitforcard()
        card_service.connection.connect()
        self.card_authentication = None
        self.card_ATR = card_service.connection.getATR()
        if DEBUG: print 'ATR: ' + toHexString(self.card_ATR)
        card_service.connection.disconnect()

        # Establish reader-centric connection
        try:
            connection = self.reader.createConnection()
            connection.connect()
            self.load_keys(connection)  # Reset reader keys to default
            return connection
        except (CardConnectionException, NoCardException):
            return None

    def read_block(self, connection, block, length, key_a_num=None, key_b_num=None):
        """Either key A or B must be specified for Mifare Classic cards"""
        valid_num = [0x00, 0x01, None]
        assert key_a_num in valid_num and key_b_num in valid_num
        if [key_a_num, key_b_num] != [None, None]:
            sector = block >> 2
            if self.card_authentication != [sector, key_a_num, key_b_num]:
                Reader._auth_mfc(connection, sector, key_a_num, key_b_num)
                self.card_authentication = [sector, key_a_num, key_b_num]
        return Reader._read_block(connection, block, length)

    @staticmethod
    def load_keys(connection, key_0=None, key_1=None):
        """Load keys into the reader. Omitting a key will revert it to the default FF key"""
        if key_0 is None: key_0 = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        if key_1 is None: key_1 = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        assert len(key_0) == 6
        assert len(key_1) == 6

        Reader._transmit(connection, PICC_CMD_LOAD_KEY_0, key_0)
        Reader._transmit(connection, PICC_CMD_LOAD_KEY_1, key_1)
        if DEBUG: print("Keys loaded into ACR122 reader")

    @staticmethod
    def get_serial_number(connection):
        """Returns card serial number in bytes"""
        return Reader._transmit(connection, PICC_CMD_GET_DATA)

    @staticmethod
    def _find_myself():
        """Iterate through the list of readers looking for the first one with matching prefix"""
        for r in readers():
            if READER_PREFIX in r.name and r.name.index(READER_PREFIX) == 0:
                return r
        raise exceptions.ReaderNotFoundException

    @staticmethod
    def _transmit(connection, command, command_vars=None):
        """Returns: data, response_code (response_code is a hex string to make it easier to work with)"""
        if command_vars is None: command_vars = []
        command_desc = command[0]
        full_command = command[1]+command_vars
        sw = [0, 0]
        data, sw[0], sw[1] = connection.transmit(full_command)
        response_code = toHexString(sw)
        if response_code == "63 00":
            raise exceptions.FailedException(command_desc)
        elif response_code == "6A 81":
            raise exceptions.NotSupportedException(command_desc)
        elif response_code != "90 00":
            raise exceptions.UnexpectedErrorCodeException(response_code, command_desc)
        return data

    @staticmethod
    def _read_block(connection, block, length):
        assert 0x00 <= block <= 0xff
        assert 0x00 <= length <= 0xff

        data = Reader._transmit(connection, PICC_CMD_READ_BLOCK, [block, length])
        # data = Reader._transmit(connection, PICC_CMD_READ_BLOCK0_DIRECT)
        if DEBUG: print('Block ' + str(block).zfill(2) + ': ' + toHexString(data))
        return data

    @staticmethod
    def _auth_mfc(connection, sector, key_a=None, key_b=None):
        """Either key A or B must be specified"""
        reader_keys = [0x00, 0x01]
        assert key_a in reader_keys or key_b in reader_keys
        assert 0x00 <= sector <= 0x3f  # 0x3f * 4 = 0xff

        if key_a is not None:
            Reader._transmit(connection, PICC_CMD_MFC_AUTH, [sector * 4, 0x60, key_a])
        if key_b is not None:
            Reader._transmit(connection, PICC_CMD_MFC_AUTH, [sector * 4, 0x61, key_b])
        if DEBUG: print("Sector " + str(sector) + " auth ok, ready to read...")
