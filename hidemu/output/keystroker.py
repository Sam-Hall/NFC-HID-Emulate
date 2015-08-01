#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# keystroker.py - Abstracted keystroke generator
#
# Structure and functionality based on Plover project features.
# May temporarily include some Plover code while I'm still getting my head around things. Even if I remove the Plover
# code I absolutely credit the authors of Plover with making the OS platform flexibility of this package possible (as
# well as my first introduction to what a well designed python application looks like).
# See plover/oslayer package... https://github.com/openstenoproject/plover/tree/b9ca01ade3/plover/oslayer
#

"""Key stroke emulation

The KeyStroker class sends text to a supported OS in the form of phony key strokes.

"""

import sys
import exceptions


if sys.platform.startswith('linux'):
    import xkeystroker as key_stroker
elif sys.platform.startswith('win32'):
    import winkeystroker as key_stroker
else:
    raise exceptions.UnsupportedPlatformException


class KeyStroker(key_stroker.KeyStroker):
    """Emulate keystrokes."""
    pass
