#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# hidemu.py - USB HID reader emulation service
#


import os
import sys
import time
import string
import logging
import traceback

logger = logging.getLogger('hidemu')  # Global logging.Logger instance (defined in main.py)

try:  # Non-standard module imports that may fail
    import singleproc
    from output import keystroker
    from smartcard.util import toHexString, toBytes, PACK, HEX, UPPERCASE, COMMA
    from smartcard.Exceptions import CardRequestTimeoutException, CardConnectionException
    from reader.exceptions import ReaderNotFoundException, FailedException, ConnectionLostException, PyScardFailure
except BaseException:
    logger.critical(traceback.format_exc())
    raise


class GracefulExit(Exception):
    """Card connection no longer valid"""
    def __init__(self, *args):
        Exception.__init__(self, "Process terminated", *args)


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

    @staticmethod
    def bytes_to_type(byte_list, data_type="hex"):
        if data_type == "ascii":
            ascii = ''.join(chr(i) for i in byte_list)
            ascii = filter(lambda x: x in string.printable, ascii)
            return ascii
        elif data_type == "int":
            return HIDEmu._little_endian_value(byte_list)
        else:
            return toHexString(byte_list, PACK)

    def _read_defined_data(self, connection):
        """Return a string list of 8 elements based on data_definition."""
        data_list = ["", "", "", "", "", "", "", ""]
        if self.data_definition is not None and self.reader.card_readable:
            data_def_list = self.data_definition
            if type(data_def_list) == dict:
                data_def_list = [data_def_list]
            for i in range(0, min(len(data_def_list), 8)):
                data_spec = data_def_list[i]
                data_key_a = data_spec.get("keyA", None)
                data_key_b = data_spec.get("keyB", None)
                data_type = data_spec.get("type", "hex")
                data_block = data_spec.get("block", 0)
                data_offset = data_spec.get("offset", 0)
                data_length = data_spec.get("length", 1)

                try:  # Read data based on the data definition
                    # Read data_block with length=data_length+data_offset and then trim everything before the offset
                    block_read = self._read_block(connection, data_block, data_length + data_offset,
                                                  data_key_a, data_key_b)[data_offset:]
                    # Process bytes based on type
                    data = HIDEmu.bytes_to_type(block_read, data_type)
                    data_list[i] = data
                except FailedException:
                    self.logger.info("Data definition #" + str(i) + " failed to apply to current card")
                    data_list[i] = ""
                except ConnectionLostException:
                    self.logger.warn("Connection lost while processing data definition.")
                    raise
        return data_list

    def _process_card(self, connection):
        """This is where the magic happens"""
        self.reader.busy_signal(connection)
        self.logger.info(self.reader.card_description + ' card detected')
        self.logger.debug('ATR: ' + toHexString(self.reader.card_ATR))
        card_serial_number = self.reader.get_serial_number(connection)
        if card_serial_number:
            self.logger.debug('UID: ' + toHexString(card_serial_number))
        else:
            card_serial_number = []
            self.logger.warn('No UID read!')

        # parse data definition and read data accordingly
        data_list = self._read_defined_data(connection)

        output_string = self.head + self.start1 + self.track1 + self.end
        if self.track2 != "": output_string += self.start2 + self.track2 + self.end
        if self.track3 != "": output_string += self.start3 + self.track3 + self.end
        output_string += self.tail

        self.key_stroker.send_string(
            self._process_output_string(output_string, card_serial_number, data_list))

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

    def _read_block(self, connection, block, length, key_a_num=None, key_b_num=None):
        ret_list = self.reader.read_block(connection, block, length, key_a_num, key_b_num)
        return ret_list

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

    def _process_output_string(self, output_string, uid_bytes, data_list=None):
        if data_list is None: data_list = ["", "", "", "", "", "", "", ""]
        if uid_bytes is None:
            uidlen = "0"
            uidint = ""
            uid = ""
        else:
            uidlen = str(len(uid_bytes))
            uidint = str(self._little_endian_value(uid_bytes))
            uid = toHexString(uid_bytes, PACK)

        return output_string.format(UIDLEN=uidlen,
                                    TYPE=self.reader.card_type,
                                    SUBTYPE=self.reader.card_subtype,
                                    UIDINT=uidint,
                                    UID=uid,
                                    CR=os.linesep,
                                    DATA=data_list[0],
                                    DATA0=data_list[0],
                                    DATA1=data_list[1],
                                    DATA2=data_list[2],
                                    DATA3=data_list[3],
                                    DATA4=data_list[4],
                                    DATA5=data_list[5],
                                    DATA6=data_list[6],
                                    DATA7=data_list[7])

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
            self.reader.set_keys(self.key1, self.key2)
            self.key_stroker = keystroker.KeyStroker()
            self.set_status('STARTED')

            try:
                conn = self.reader.connect(1, False)
            except CardRequestTimeoutException:
                conn = None

            while self.running:
                try:
                    if not self.reader.exists():
                        raise ReaderNotFoundException
                    if conn is None: conn = self.reader.connect()
                    if conn is not None:
                        self._process_card(conn)
                except CardRequestTimeoutException:
                    # Connection not established within the specified time frame (normal behaviour)
                    pass
                except FailedException, args:
                    # An error occurred while reading card
                    self.logger.warn("Card processing failed: " + str(args))
                except ConnectionLostException, args:
                    # Card likely removed too quickly
                    self.logger.warn("Card removed too soon: " + str(args))
                except CardConnectionException:
                    # Unexpected but recoverable error, possibly caused by a software conflict
                    self.logger.error(traceback.format_exc())
                    self.reader.error_signal(duration=6)
                conn = None
        except ReaderNotFoundException:
            self.logger.critical('Reader disconnected')
        except KeyboardInterrupt:
            self.logger.warn('Terminated by user')
        except GracefulExit:
            self.logger.warn('Process terminated')
        except PyScardFailure:
            self.logger.critical('PCSC service failure, check dependencies including version numbers.')
            raise
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
