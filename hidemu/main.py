#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - USB HID reader emulation app
#

import os
from hidemu.reader import autodetect
from hidemu.output import keystroker


def main():
    """Launch app"""
    # TODO: Add a systray GUI component and reader polling loop (or work out how to listen for a new card)
    # TODO: Ensure only one instance is running at a time.
    reader = autodetect.Reader()
    key_stroker = keystroker.KeyStroker()
    sn = reader.get_serial_number()
    if sn:
        # TODO: Detect and correctly report the Mifare UID byte size
        key_stroker.send_string('#4MF^' + sn + ';' + os.linesep)
    print(sn)

if __name__ == '__main__':
    main()
