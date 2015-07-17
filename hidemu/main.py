#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - USB HID reader emulation app
#

import hidemu.reader.autodetect
import hidemu.output.keystroker


def main():
    """Launch app"""
    # TODO: Add a systray GUI component and reader polling loop (or work out how to listen for a new card)
    # TODO: Ensure only one instance is running at a time.
    reader = hidemu.reader.autodetect.Reader()
    key_stroker = hidemu.output.keystroker.KeyStroker()
    sn = reader.get_serial_number()
    if sn:
        # TODO: Detect and correctly report the Mifare UID byte size
        # TODO: Confirm \r\n is cross platform enough, and if not do something platform detecty
        key_stroker.send_string('#4MF^' + sn + ';\r\n')
    print(sn)

if __name__ == '__main__':
    main()
