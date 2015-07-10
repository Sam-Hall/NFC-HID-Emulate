#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - USB HID reader emulation app
#
#

import hidemu.reader.autodetect


def main():
    """Launch app"""
    # TODO: Create a cross platform output package

    # TODO: Add a systray GUI component and reader polling loop (or work out how to listen for a new card)

    # TODO: Ensure only one instance is running at a time.

    reader = hidemu.reader.autodetect.Reader()
    sn = reader.get_serial_number()
    print(sn)


if __name__ == '__main__':
    main()

