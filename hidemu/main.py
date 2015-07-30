#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - starts the service
#

from hidemu import HidEmu


def main():
    """Start the service"""
    # TODO: Design it to run in the background or as a service with command line args for any user defined options
    # TODO: Output format configurable from command line args
    # Support: card type, UID (hex or decimal), given value from binary read with length and offset
    hid_emu = HidEmu()
    hid_emu.start_service()


if __name__ == '__main__':
    main()

