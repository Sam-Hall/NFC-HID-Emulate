#!/usr/bin/env python
# Copyright (c) 2015 Sam Hall, Charles Darwin University
# See LICENSE.txt for details.
#
# winkeystroker.py

"""KeyStroker class for Windows

Windows module for emulating keystrokes required to output specified characters. This is about as simple as it gets.
Probably could do with some error handling though as long as you stick to using the public methods on Windows platform
it should be pretty hard to break. That said, it probably doesn't support unicode characters since it's using ANSI
specific WinAPI functions.

"""

from ctypes import windll

# VkKeyScanA high order flag key codes (SHIFT, CTRL, ALT)
MODIFIER_KEYCODE = {1: 16,
                    2: 17,
                    4: 18}


class KeyStroker:
    """Emulate key strokes required to output specified characters"""

    def __init__(self):
        pass

    def send_string(self, string):
        """Emulate typing a string"""
        for character in string:
            try:
                self.send_character(character)
            except KeyError:
                pass  # Invalid character

    def send_character(self, character):
        """Emulate typing a character"""
        vk_code, modifiers = self._vk_and_modifiers_from_char(character[0])
        self._apply_modifiers(modifiers)
        self._key_down(vk_code)
        self._key_up(vk_code)
        self._release_modifiers(modifiers)

    def _apply_modifiers(self, modifiers):
        for bit in self._modifier_bit_split(modifiers):
            self._key_down(MODIFIER_KEYCODE[bit])

    def _release_modifiers(self, modifiers):
        for bit in self._modifier_bit_split(modifiers):
            self._key_up(MODIFIER_KEYCODE[bit])

    @staticmethod
    def _modifier_bit_split(modifiers):
        while modifiers:
            bit = modifiers & (~modifiers+1)
            yield bit
            modifiers ^= bit

    @staticmethod
    def _key_down(bvk):
        bscan = windll.user32.MapVirtualKeyA(bvk, 0)
        windll.user32.keybd_event(bvk, bscan, 0, 0)

    @staticmethod
    def _key_up(bvk):
        bscan = windll.user32.MapVirtualKeyA(bvk, 0)
        windll.user32.keybd_event(bvk, bscan, 0x0002, 0)

    @staticmethod
    def _vk_and_modifiers_from_char(key_char):
        word_up = windll.user32.VkKeyScanA(ord(key_char))
        vk = word_up & 0xff
        modifiers = (word_up & 0xff00) >> 8
        return vk, modifiers
