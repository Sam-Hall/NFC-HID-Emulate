#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# xkeystroker.py - got some clues for this from pykey... http://www.shallowsky.com/software/crikey/pykey-0.1
# If fake_input turns out to be less than desirable, see the pykey Xlib event alternative (same as Plover used).

"""KeyStroker class for Linux (using Xlib)

Simple keystroke emulation module.

"""

import time
from Xlib import display, X, XK
from Xlib.ext.xtest import fake_input

SPECIAL_KEYSYM = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Linefeed",
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
}


class KeyStroker:
    """Emulate key strokes"""

    def __init__(self, logger=None):
        """Refer some useful Xlib objects"""
        self.logger = logger
        self.display = display.Display()
        self.shift_keycode = self.display.keysym_to_keycode(XK.XK_Shift_L)

    def send_string(self, string):
        """Emulate typing a string"""
        for character in string:
            self.send_character(character)

    def send_character(self, character):
        """Emulate typing a character"""
        keycode, shifted = self._to_keycode(character)

        # Press
        if shifted:
            self._key_down(self.shift_keycode)
        self._key_down(keycode)
        self.display.sync()

        time.sleep(0.001)

        # Release
        self._key_up(keycode)
        if shifted:
            self._key_up(self.shift_keycode)
        self.display.sync()

    def _key_down(self, keycode):
        fake_input(self.display, X.KeyPress, keycode)

    def _key_up(self, keycode):
        fake_input(self.display, X.KeyRelease, keycode)

    def _to_keycode(self, character):
        shifted = self._is_shifted(character)
        keysym = XK.string_to_keysym(character)
        if keysym == 0:
            keysym = XK.string_to_keysym(SPECIAL_KEYSYM[character])
        return self.display.keysym_to_keycode(keysym), shifted

    @staticmethod
    def _is_shifted(character):
        if character.isupper():
            return True
        if character in '~!@#$%^&*()_+{}|:"<>?':
            return True
        return False
