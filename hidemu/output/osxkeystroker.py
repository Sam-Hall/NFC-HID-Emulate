#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# osxkeystroker.py - based on Plover modules

"""KeyStroker class for OSX

Essentially a simplified module based on plover/oslayer/osxkeyboardcontrol for the sole purpose of emulating keystrokes.

"""

import osxkeyboardcontrol  # Plover code


class KeyStroker:
    """Emulate key strokes"""

    def __init__(self):
        # TODO: replace Plover modules with internal methods...
        self.plover_kb_emu = osxkeyboardcontrol.KeyboardEmulation()

    def send_string(self, string):
        """Emulate typing a string"""
        self.plover_kb_emu.send_string(string)

    def send_key(self, character, sync=1):
        """Emulate typing a character (optionally syncing the display)"""
        # TODO: in this case, this seems a bit silly, do I really need send_key?
        self.send_string(character)
