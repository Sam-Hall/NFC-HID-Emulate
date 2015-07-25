#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - USB HID reader emulation app
#

import os
import logging
import traceback
import singleproc

# Logging Config
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('hidemu.log')
handler.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    from hidemu.reader import autodetect
    from hidemu.output import keystroker
    from smartcard.util import toHexString, toBytes
    from smartcard.Exceptions import CardRequestTimeoutException
except BaseException:
    logger.critical(traceback.format_exc())
    raise


def main():
    """Launch app"""
    # TODO: Add a systray GUI component and reader polling loop (or work out how to listen for a new card)
    # TODO: Decide how to cope with Exceptions generated when other software is manipulating the reader
    # TODO: Output format configurable from a ini file.
    # Support: card type, UID (hex or decimal), given value from binary read with length and offset

    logger.info('SERVICE STARTING')
    proc_lock = None
    try:
        proc_lock = singleproc.create_lock("hidemu")
        reader = autodetect.Reader()
        key_stroker = keystroker.KeyStroker()

        try:
            conn = reader.connect(1, False)
        except CardRequestTimeoutException:
            conn = None

        while 1:
            try:
                if conn is None: conn = reader.connect()
                if conn is not None:
                    logger.info(reader.card_description + ' card detected: ' + toHexString(reader.card_ATR))

                    sn = reader.get_serial_number(conn)
                    if sn:
                        logger.info('Card UID: ' + toHexString(sn))
                        sn_str = ''.join('{:02x}'.format(x) for x in sn).upper()
                        key_stroker.send_string('#' + str(len(sn)) + reader.card_type + '^' + sn_str + ';' + os.linesep)
                        read_card_test(reader, conn)
                    else:
                        logger.warn('No UID read!')
                    conn.disconnect()
            except CardRequestTimeoutException:
                pass
            conn = None
    except singleproc.AlreadyLocked:
        logger.info('Another instance is already running')
    except KeyboardInterrupt:
        logger.info('Terminated by user')
    except BaseException:
        logger.critical(traceback.format_exc())
        raise
    finally:
        singleproc.unlock(proc_lock)
        logger.info('SERVICE STOPPED')


def read_card_test(reader, connection):
    if not reader.card_readable:
        logger.info('Card read not supported')
    else:

        start_sector = 0
        if reader.card_authable: reader.load_keys(connection, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

        for sector in range(start_sector, 16):
            block = sector * 4
            for b in range(block, block + 4):
                try:
                    data = reader.read_block(connection, b, 0x10, 0x00)
                    logger.debug('Block ' + str(b).zfill(2) + ': ' + ''.join('{:02x}'.format(x) for x in data).upper())
                except Exception as e:
                    logger.debug('Failed block read (' + str(b).zfill(2) + '): ' + type(e).__name__ + str(e))


if __name__ == '__main__':
    main()
