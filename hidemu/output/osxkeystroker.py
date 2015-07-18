#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# osxkeystroker.py - built on Plover module osxkeyboardcontrol

"""KeyStroker class for OSX

Wrapper on plover/oslayer/osxkeyboardcontrol with functionality cut down for the sole purpose of emulating keystrokes.
Until I manage to get the project to build on OSX, this is about the best I can do for the platform.

"""

import osxkeyboardcontrol  # Plover module


class KeyStroker:
    """Emulate key strokes"""

    def __init__(self):
        # TODO: replace Plover modules with internal methods...
        self.plover_kb_emu = osxkeyboardcontrol.KeyboardEmulation()

    def send_string(self, string):
        """Emulate typing a string"""
        self.plover_kb_emu.send_string(string)

    def send_character(self, character):
        """Emulate typing a character"""
        # TODO: in this case, this seems a bit silly, do I really need send_character?
        self.send_string(character)
