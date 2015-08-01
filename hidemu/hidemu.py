#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# hidemu.py - USB HID reader emulation service
#


import os
import sys
import time
import json
import logging
import traceback

logger = logging.getLogger('hidemu')  # Global logging.Logger instance (defined in main.py)

try:  # Non-standard module imports that may fail
    import singleproc
    from output import keystroker
    from smartcard.util import toHexString, toBytes
    from smartcard.Exceptions import CardRequestTimeoutException, CardConnectionException
    from reader.exceptions import ReaderNotFoundException
except BaseException:
    logger.critical(traceback.format_exc())
    raise


OUTPUT_SUBSTITUTIONS = ['UIDLEN', 'TYPE', 'SUBTYPE', 'UIDINT', 'UID', 'CR', 'DATA']


class HIDEmu:
    def __init__(self,
                 head="",
                 start1="%", start2=";", start3="+",
                 track1="{UIDLEN}{TYPE}^{UIDINT}",track2="",track3="",
                 end="?",
                 tail="{CR}",
                 key1="FFFFFFFFFFFF",
                 key2="FFFFFFFFFFFF",
                 data_definition=None):
        self.running = False
        self.name = 'HIDEmu'
        self.status = 'INIT'
        self.logger = logging.getLogger('hidemu')     # Use the global logger internally
        self.reader = None       # hidemu.reader.Reader instance (see reader.ReaderBase)
        self.key_stroker = None  # hidemu.output.keystroker.KeyStroker instance

        # Process configuration settings
        self.head = head
        self.track1 = track1
        self.track2 = track2
        self.track3 = track3
        self.start1 = start1
        self.start2 = start2
        self.start3 = start3
        self.end = end
        self.tail = tail
        self.key1 = key1
        self.key2 = key2
        self.data_definition = data_definition

    def _read_data(self, connection):
        data_list = []
        if self.data_definition is not None:
            data_def = self.data_definition
            if type(data_def) == dict:
                data_def = [data_def]
            for i in range(0, min(len(data_def), 8)):
                data_spec = data_def[i]
                data_auth = data_spec.get("auth1", None)
                data_type = data_spec.get("type", None)
                data_block = data_spec.get("block", None)
                data_length = data_spec.get("length", None)
                print "{0} {1} {2} {3}".format(data_auth, data_type, data_block, data_length)
            return self._read_data_bytes(connection, data_block, data_length)

        return data_list

    def _process_card(self, connection):
        """This is where the magic happens"""
        self.reader.busy_signal(connection)
        self.logger.debug(self.reader.card_description + ' card detected: ' + toHexString(self.reader.card_ATR))
        sn = self.reader.get_serial_number(connection)
        if sn:
            self.logger.debug('Card UID: ' + toHexString(sn))
            # self._read_card_test(connection)
            # TODO: parse data definition json and read data accordinly
            data = self._read_data_bytes(connection, 0x03, 0x04)

            output_string = self.head + self.start1 + self.track1 + self.end
            if self.track2 != "":
                output_string = self.start2 + self.track2 + self.end
            if self.track3 != "":
                output_string = self.start3 + self.track3 + self.end
            output_string += self.tail

            self.key_stroker.send_string(
                self._process_output_string(output_string, sn))
        else:
            self.logger.warn('No UID read!')
        self.reader.ready_signal(connection)
        connection.disconnect()

    def _wait_for_reader(self):
        self.logger.info("Waiting for compatible reader...")
        busy_error = False  # Flag to avoid logging the Reader Busy message multiple times
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

    def _read_data_bytes(self, connection, block, length, offset=0, key_a_num=None, key_b_num=None):
        return [0x10, 0x00, 0x00, 0x00]  # TODO: finish this

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

    @staticmethod
    def _little_endian_value(byte_list):
        little_endian_value = 0
        for i in range(0, len(byte_list)):
            shift = i * 8
            little_endian_value += byte_list[i] << shift
        return little_endian_value

    @staticmethod
    def _to_mifare_key(value):
        if len(value) != 12: raise ValueError
        int(value, 16)  # also throws ValueError if not a hex string
        return toBytes(value)

    def _process_output_string(self, output_string, uid_bytes,
                               data0="", data1="", data2="", data3="", data4="", data5="", data6="", data7=""):
        if uid_bytes is None:
            uidlen = "0"
            uidint = ""
            uid = ""
        else:
            uidlen = str(len(uid_bytes))
            uidint = str(self._little_endian_value(uid_bytes))
            uid = toHexString(uid_bytes,1)

        return output_string.format(UIDLEN=uidlen,
                                    TYPE=self.reader.card_type,
                                    SUBTYPE=self.reader.card_subtype,
                                    UIDINT=uidint,
                                    UID=uid,
                                    CR=os.linesep, DATA="",
                                    DATA0="", DATA1="", DATA2="", DATA3="", DATA4="", DATA5="", DATA6="", DATA7="")

    def set_status(self, status):
        self.status = status
        self.logger.info('{0} {1}'.format(self.name, self.status))

    def start_daemon(self):
        self.set_status('STARTING')
        try:
            process_lock = singleproc.create_lock("hidemu")
        except singleproc.AlreadyLocked:
            self.logger.error('Attempted to start while another instance is already running')
            sys.exit(-1)
        try:
            self.running = True
            self.reader = self._wait_for_reader()
            self.key_stroker = keystroker.KeyStroker()
            self.set_status('STARTED')

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
            self.logger.warn('Terminated by user')
        except BaseException:
            self.logger.critical(traceback.format_exc())
            raise
        finally:
            singleproc.unlock(process_lock)
            self.set_status('STOPPED')

    def stop_daemon(self):
        """Gracefully stop the daemon"""
        # TODO: Research into SIGTERM handler to trigger this and test for cross platform support
        self.running = False
