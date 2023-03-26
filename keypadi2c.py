# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 River Wang
#
# SPDX-License-Identifier: MIT
"""
`keypadi2c`
================================================================================

A CircuitPython keypad library that supports MCP I2C IO expanders.

* Author(s): River Wang

Implementation Notes
--------------------

**Hardware:**
* Work with I2C IO Expanders especially:
* MCP23017 <https://www.adafruit.com/product/732>
* MCP23008 <https://www.adafruit.com/product/593>

**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards <https://circuitpython.org/downloads>
* This library depends on `keypad` module to work, which is native to CircuitPython 7+
* You will also need `MCP230xx` library <https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx>

"""

# imports
import keypad

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/urfdvw/CircuitPython_keypadi2c.git"


class ModeFilter:
    # when False is active, filter via or to filter out accident active
    def __init__(self, N):
        self.values = [None for i in range(N)]
        self.counter = {None: N}

    def __call__(self, val):
        old = self.values.pop(0)
        self.values.append(val)

        if val in self.counter:
            self.counter[val] += 1
        else:
            self.counter[val] = 1

        self.counter[old] -= 1
        if self.counter[old] == 0:
            self.counter.pop(old)

        return max(((v, k) for k, v in self.counter.items() if k is not None))[-1]


class EventQueue:
    def __init__(self):
        self.data = []

    def append(self, given):
        self.data.append(given)

    def get(self):
        if self.data:
            return self.data.pop(0)
        else:
            return None

    def clear(self):
        self.data = []

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)


class I2CKeys:
    def __init__(self, mcp, nbits, code_shift=0):
        # in take
        self.mcp = mcp
        self.nbits = nbits
        self.code_shift = code_shift

        # configure
        self.mcp.gppu = (1 << nbits) - 1

        # constants
        self.power2 = [1 << i for i in range(self.nbits)]
        self.codes = {self.power2[i]: i for i in range(self.nbits)}

        # event queue
        self._events = EventQueue()

        # init status
        self.last_keys = (1 << nbits) - 1

        # debouncing
        self.filter = ModeFilter(3)

    def search_code(self, number):
        if number == 0:
            return []
        if number in self.codes:
            return [self.codes[number] + self.code_shift]
        else:
            return [
                i + self.code_shift
                for i in range(self.nbits)
                if number & self.power2[i]
            ]

    @property
    def events(self):
        # get current input
        try:
            # try because failed before
            keys = self.filter(self.mcp.gpio)
            # print(keys)
        except Exception as e:
            print(e)
            return self._events

        # push events into queue
        for k in self.search_code(~keys & (self.last_keys ^ keys)):
            self._events.append(keypad.Event(key_number=k, pressed=True))
        for k in self.search_code(keys & (self.last_keys ^ keys)):
            self._events.append(keypad.Event(key_number=k, pressed=False))

        # update status
        self.last_keys = keys
        return self._events


class I2CKeyPad:
    def __init__(self, key_secs):
        self.key_secs = key_secs
        self._events = EventQueue()

    @property
    def events(self):
        for sec in self.key_secs:
            while event := sec.events.get():
                self._events.append(event)
        return self._events
