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
from smartcard.Exceptions import CardConnectionException, NoCardException

READER_PREFIX = "ACS ACR122"

PICC_CMD_GET_DATA = [0xFF, 0xCA, 0x00, 0x00, 0x00]


def find_myself():
    """Iterate through the list of readers looking for the first one with matching prefix"""
    for r in readers():
        if READER_PREFIX in str(r) and str(r).index(READER_PREFIX) == 0:
            return r
    raise exceptions.ReaderNotFoundException


class Reader:
    """ACR122 reader class

    Built for ACR122U but may support similar USB models"""
    # TODO: Find out what happens if reader disconnects during program execution and how to recover from that

    def __init__(self):
        # TODO: Do we establish connection to the reader now? (i.e. to listen for new card events)

        self.reader = find_myself()
        pass

    def get_serial_number(self):
        """Returns card serial number or None if no card is detected"""
        # TODO: Return the serial number as an actual number

        try:
            connection = self.reader.createConnection()
            connection.connect()
            sw = [0, 0]
            data, sw[0], sw[1] = connection.transmit(PICC_CMD_GET_DATA)
            response_code = ''.join('{:02x}'.format(x) for x in sw).upper()

            if response_code == "9000":
                return ''.join('{:02x}'.format(x) for x in data).upper()
            elif response_code == "6300":
                raise exceptions.CSNFailedException
            elif response_code == "6A81":
                raise exceptions.CSNNotSupportedException
            raise exceptions.CSNUnexpectedException
        except (CardConnectionException, NoCardException):
            return None
