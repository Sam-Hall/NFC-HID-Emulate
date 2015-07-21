#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - USB HID reader emulation app
#

import os
from hidemu.reader import autodetect
from hidemu.output import keystroker
from smartcard.Exceptions import CardRequestTimeoutException


def main():
    """Launch app"""
    # TODO: Add a systray GUI component and reader polling loop (or work out how to listen for a new card)
    # TODO: Ensure only one instance is running at a time.
    # TODO: Output format configurable from a ini file.
    # Support: card type, UID (hex or decimal), given value from binary read with length and offset

    reader = autodetect.Reader()
    key_stroker = keystroker.KeyStroker()

    try:
        conn = reader.connect(1, False)
    except CardRequestTimeoutException:
        conn = None

    while 1:
        while conn is None:
            try:
                conn = reader.connect()

                sn = reader.get_serial_number(conn)

                if sn:
                    sn_str = ''.join('{:02x}'.format(x) for x in sn).upper()
                    key_stroker.send_string('#' + str(len(sn)) + 'MF^' + sn_str + ';' + os.linesep)
                    print('UID: ' + sn_str)
                    # mfc1k_read_test(reader, conn)
                else:
                    print('No UID read!')
            except CardRequestTimeoutException:
                conn = None

        conn.disconnect()
        conn = None


def mfc1k_read_test(reader, connection):
    # Mifare Classic 1k read test
    reader.load_keys(connection, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    # reader.load_keys(conn, [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5])
    for sector in range(0, 16):
        block = sector * 4
        for b in range(block, block + 4):
            try:
                data = reader.read_block(connection, b, 0x10, 0x00)
                print('Block ' + str(b).zfill(2) + ': ' + ''.join('{:02x}'.format(x) for x in data).upper())
            except Exception as e:
                print('Failed block read (' + str(b).zfill(2) + '): ' + type(e).__name__ + str(e))


if __name__ == '__main__':
    main()

