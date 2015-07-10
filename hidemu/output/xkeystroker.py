#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# xkeystroker.py - based on Plover (and in turn AutoKey and pyxhook)

"""KeyStroker class for Linux (using Xlib)

Essentially a simplified module based on plover/oslayer/xkeyboardcontrol for the sole purpose of emulating keystrokes.

"""


import xkeyboardcontrol  # Plover code

from Xlib import display, X
from Xlib.protocol import event


class KeyStroker:
    """Emulate key strokes"""

    def __init__(self):
        """Refer some useful Xlib objects"""
        self.display = display.Display()
        self.modifier_mapping = self.display.get_modifier_mapping()
        self.time = 0
        # TODO: replace Plover modules with internal methods...
        self.plover_kb_emu = xkeyboardcontrol.KeyboardEmulation()

    def send_string(self, string):
        """Emulate typing a string"""
        for character in string:
            self.send_key(character, 0)
        self.display.sync()

    def send_key(self, character, sync=1):
        """Emulate typing a character (optionally syncing the display)"""
        key_code, modifiers = self.plover_kb_emu._keysym_to_keycode_and_modifiers(ord(character[0]))

        if key_code:
            self.plover_kb_emu._send_key_event(key_code, modifiers, event.KeyPress)
            self.plover_kb_emu._send_key_event(key_code, modifiers, event.KeyRelease)
        else:
            # Non-printable character?
            print("NPC(" + str(ord(character)) + "):" + character)

        # TODO: newline is currently buggy, why?

        if sync:
            self.display.sync()
