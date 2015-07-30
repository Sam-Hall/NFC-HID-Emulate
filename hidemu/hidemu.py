#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# hidemu.py - USB HID reader emulation service
#

import os
import sys
import time
import logging
import traceback
import argparse


logger = None  # Reserved for global logging.Logger instance


def setup_global_logger():
    """Logging config, need to set this up before attempting to import non-standard modules"""
    global logger
    logformat = '%(asctime)s - %(levelname)s: %(message)s'
    logfile = 'hidemu.log'

    # Levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    logfile_level = logging.INFO
    console_level = logging.NOTSET
    # console_level = logging.DEBUG

    logger = logging.getLogger('hidemu')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(logformat)

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logfile_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_level > logging.NOTSET:
        cons_handler = logging.StreamHandler()
        cons_handler.setLevel(console_level)
        cons_handler.setFormatter(formatter)
        logger.addHandler(cons_handler)

setup_global_logger()

# Module imports that may fail (non-standard modules)
try:
    import singleproc
    from output import keystroker
    from smartcard.util import toHexString, toBytes
    from smartcard.Exceptions import CardRequestTimeoutException, CardConnectionException
    from reader.exceptions import ReaderNotFoundException
except BaseException:
    logger.critical(traceback.format_exc())
    raise


class HidEmu:
    def __init__(self):
        global logger
        self.running = False
        self.logger = logger     # Use the global logger internally
        self.reader = None       # hidemu.reader.Reader instance (see reader.ReaderBase)
        self.key_stroker = None  # hidemu.output.keystroker.KeyStroker instance

        # User configurable settings (work in progress)
        args = argparse.ArgumentParser(description='Human Interface Device emulator for NFC card reader.')
        args.add_argument('--start1', help='Pseudo-track 1 start sentinel')
        args.add_argument('--start2', help='Pseudo-track 2 start sentinel')
        args.add_argument('--start3', help='Pseudo-track 3 start sentinel')
        args.add_argument('--end', help='Stop sentinel')

    def _process_card(self, connection):
        """This is where the magic happens"""
        self.reader.busy_signal(connection)
        self.logger.debug(self.reader.card_description + ' card detected: ' + toHexString(self.reader.card_ATR))
        sn = self.reader.get_serial_number(connection)
        if sn:
            self.logger.debug('Card UID: ' + toHexString(sn))
            sn_str = ''.join('{:02x}'.format(x) for x in sn).upper()
            # self._read_card_test(connection)
            self.key_stroker.send_string('#' + str(len(sn)) + self.reader.card_type + '^' + sn_str + ';' + os.linesep)
        else:
            logger.warn('No UID read!')
        self.reader.ready_signal(connection)
        connection.disconnect()

    def _wait_for_reader(self):
        self.logger.info("Waiting for compatible reader...")
        busy_error = False  # flag to avoid logging the Reader Busy message multiple times
        while 1:
            try:
                time.sleep(1)
                from reader import autodetect
                self.logger.info("Reader found")
                return autodetect.Reader()
            except ReaderNotFoundException:
                pass
            except CardConnectionException:
                if not busy_error:
                    self.logger.warn("Reader appears busy, this may indicate another piece of software is using it.")
                    busy_error = True

    def _read_card_test(self, connection):
        if not self.reader.card_readable:
            self.logger.info('Card read not supported')
        else:

            start_sector = 0
            if self.reader.card_authable: self.reader.load_keys(connection, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

            for sector in range(start_sector, 16):
                block = sector * 4
                for b in range(block, block + 4):
                    try:
                        data = self.reader.read_block(connection, b, 0x10, 0x00)
                        self.logger.debug(
                            'Block ' + str(b).zfill(2) + ': ' + ''.join('{:02x}'.format(x) for x in data).upper())
                    except Exception as e:
                        self.logger.debug('Failed block read (' + str(b).zfill(2) + '): ' + type(e).__name__ + str(e))

    def start_service(self):
        try:
            process_lock = singleproc.create_lock("hidemu")
        except singleproc.AlreadyLocked:
            logger.error('Attempted to start while another instance is already running')
            sys.exit(-1)
        try:
            self.running = True
            self.reader = self._wait_for_reader()
            self.logger.info('SERVICE STARTING')
            self.key_stroker = keystroker.KeyStroker()

            try:
                conn = self.reader.connect(1, False)
            except CardRequestTimeoutException:
                conn = None

            while self.running:
                try:
                    if conn is None: conn = self.reader.connect()
                    if conn is not None:
                        self._process_card(conn)
                except CardRequestTimeoutException:
                    # Connection not established within the specified time frame (normal behaviour)
                    pass
                except CardConnectionException:
                    # Unexpected but recoverable error, possibly caused by a software conflict
                    self.logger.error(traceback.format_exc())
                    self.reader.error_signal(duration=6)
                conn = None
        except KeyboardInterrupt:
            logger.warn('Terminated by user')
        except BaseException:
            logger.critial(traceback.format_exc())
            raise
        finally:
            singleproc.unlock(process_lock)
            logger.info('SERVICE STOPPED')

    def stop_service(self):
        """Gracefully stop the service"""
        # TODO: Research into SIGTERM handler to trigger this and test for cross platform support
        self.running = False
