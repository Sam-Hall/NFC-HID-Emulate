#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# main.py - validate args, establish a logger and then start HIDEmu
#


import os
import logging
import json
import argparse

from hidemu import HIDEmu

# These values are also used setup.py
__app_name__ = "ACR122 HID Emulator"
__version__ = "0.2.01"  # TODO: Update this before build


def setup_logger(logger_name, log_filename):
    """Configures and returns a logging.Logger instance"""
    logformat = "%(asctime)s - %(levelname)s: %(message)s"

    # Levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    logfile_level = logging.INFO
    console_level = logging.NOTSET
    console_level = logging.DEBUG  # TODO: Comment this out before build

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(logformat)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logfile_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_level > logging.NOTSET:
        cons_handler = logging.StreamHandler()
        cons_handler.setLevel(console_level)
        cons_handler.setFormatter(formatter)
        logger.addHandler(cons_handler)
    return logger


def setup_arg_parser():
    """User configurable settings (work in progress)"""
    parser = argparse.ArgumentParser(description="Human Interface Device emulator for NFC card reader. \n"
                                     "Behaves like a USB HID magnetic stripe reader.",
                                     formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument("-h", "--help",
                        action="help", default=argparse.SUPPRESS,
                        help="Show this help message and exit.")
    parser.add_argument("-V", "--version",
                        action="version",
                        help="Show version number and exit.",
                        version=__app_name__ + " " + __version__)
    parser.add_argument("-hd", "--head", type=substitution_string_arg,
                        help="String to output before pseduo-tracks (optional).",
                        default="#")  # TODO: Change to empty string before build
    parser.add_argument("-s1", "--start1", type=substitution_string_arg,
                        help="Pseudo-track 1 start sentinel. \n\nDEFAULT: %%",
                        default="%")
    parser.add_argument("-s2", "--start2", type=substitution_string_arg,
                        help="Pseudo-track 2 start sentinel. \n\nDEFAULT: ;",
                        default=";")
    parser.add_argument("-s3", "--start3", type=substitution_string_arg,
                        help="Pseudo-track 3 start sentinel. \n\nDEFAULT: +",
                        default="+")
    parser.add_argument("-t1", "--track1", type=substitution_string_arg,
                        help="Pseudo-track 1 data. \n"
                        "\n"
                        "DEFAULT: {UIDLEN}{TYPE}^{UIDINT}\n"
                        "\n"
                        "SUBSTITUTIONS:\n"
                        "  * {UIDLEN} byte length of card UID\n"
                        "  * {TYPE} short card-type code\n"
                        "  * {SUBTYPE} card subtype code\n"
                        "  * {UIDINT} card UID as little endian base 10 value\n"
                        "  * {UID} card UID as raw hex byte string\n"
                        "  * {CR} line separator (OS specific)\n"
                        # "  * {DATA} equates to {DATA0}\n"
                        # "  * {DATA<n>} data defined by DATADEFINITION element n\n"
                        "  * Use \"{{\" to output \"{\" and \"}}\" to output \"}\"\n",
                        default="{UIDLEN}{TYPE}^{UIDINT}")
    # parser.add_argument("-t2", "--track2", type=substitution_string_arg,
    #                     help="Pseudo-track 2 data. \n"
    #                     "\n"
    #                     "Optional, see TRACK1. Numerical values recommended\n"
    #                     "here for magstripe application compatibilty reasons.")
    # parser.add_argument("-t3", "--track3", type=substitution_string_arg,
    #                     help="Pseudo-track 3 data. \n"
    #                     "\n"
    #                     "Optional, see TRACK1. Numerical values recommended\n"
    #                     "here for magstripe application compatibilty reasons.")
    parser.add_argument("-e", "--end", type=substitution_string_arg,
                        help="\nPseudo-track end sentinel. \n\nDEFAULT: ?",
                        default="?")
    parser.add_argument("-tl", "--tail", type=substitution_string_arg,
                        help="String to output after pseduo-tracks (optional). \n\nDEFAULT: {CR}",
                        default="{CR}")
    # parser.add_argument("-k1", "--key1", type=mifare_key_arg,
    #                     help="Mifare Key 1 - six bytes. \n\nDEFAULT: FFFFFFFFFFFF",
    #                     default="FFFFFFFFFFFF")
    # parser.add_argument("-k2", "--key2", type=mifare_key_arg,
    #                     help="Mifare Key 2 - six bytes. \n\nDEFAULT: FFFFFFFFFFFF",
    #                     default="FFFFFFFFFFFF")
    # parser.add_argument("-kf", "--keyfile",
    #                     help="Mifare Key file - two lines (KEY1 and KEY2).\n"
    #                     "Takes priority over KEY1 and KEY2 when specified.")
    # parser.add_argument("-dd", "--datadefinition", type=json.loads,
    #                     help="Data definition - json string. Maximum of 8 elements. \n"
    #                     "\n"
    #                     "E.G. \n'[{\"auth\":\"<A<0|1>|B<0|1>>\",\"type\":\"<int|ascii|hex>\",\n"
    #                     "\"mad\":\"HHHH\",\"block\":nn,\"offset\":nn,\"length\":nn}]'\n"
    #                     "\n"
    #                     "NOTES:\n  * \"auth\" may be optional depending on card type.\n"
    #                     "  * \"mad\" optional. 2 byte MAD entry hex string.\n"
    #                     "  * \"block\" absolute or offset (when \"mad\" present).\n"
    #                     "  * \"offset\" is optional (default is 0).\n"
    #                     "  * \"type\":\"int\" recommended for track 2 & 3 data for\n"
    #                     "    magstripe application compatibilty reasons.")
    parser.add_argument("-l", "--log", type=log_file_arg,
                        help="\nLog file. \n\nDEFAULT: hidemu.log",
                        default="hidemu.log")
    return parser


def mifare_key_arg(value):
    """Validate Mifare key hex string"""
    if len(value) != 12: raise ValueError
    int(value, 16)  # also throws ValueError if not a hex string
    return value


def log_file_arg(file_name):
    """Validate log file is writable"""
    try:  # Test write a single newline character to the file
        with open(file_name, "ab+") as file_handle:
            file_handle.write("\x0D")
            file_handle.close()
    except IOError:
        raise ValueError

    try:  # Attempt to clean up the character
        with open(file_name, "rb+") as file_handle:
            file_handle.seek(-1, os.SEEK_END)
            file_handle.truncate()
            file_handle.close()
    except IOError:
        pass  # Cleanup isn't a requirement for logging and fails on /dev/null for instance

    return file_name


def substitution_string_arg(string):
    try:  # Would love to find a more dynamic way to validate substitutions
        string.format(UIDLEN="", TYPE="", SUBTYPE="", UIDINT="", UID="", CR="", DATA="",
                      DATA0="", DATA1="", DATA2="", DATA3="", DATA4="", DATA5="", DATA6="", DATA7="")
    except KeyError:
        raise ValueError
    return string


def main():
    """Validate args, initialise logger and start up HIDEmu"""
    parser = setup_arg_parser()
    # For testing json parser...
    # -dd '[{"auth":"A0","type":"int","mad":"HHHH","block":12,"offset":1,"length":4}]'
    args = parser.parse_args()
    hidemu_logger = setup_logger('hidemu', args.log)

    hid_emu = HIDEmu(head=args.head,
                     start1=args.start1,
                     start2=args.start2,
                     start3=args.start3,
                     track1=args.track1,
                     end=args.end)
    hid_emu.start_daemon()


if __name__ == '__main__':
    main()

