import keypad

class EventQueue:
    def __init__(self):
        self.data = []

    def get_into(self, given):
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
            keys = self.mcp.gpio
        except Exception as e:
            print(e)
            return self._events
        # push events into queue
        for k in self.search_code(~keys & (self.last_keys ^ keys)):
            self._events.get_into(
                keypad.Event(key_number=k, pressed=True)
            )
        for k in self.search_code(keys & (self.last_keys ^ keys)):
            self._events.get_into(
                keypad.Event(key_number=k, pressed=False)
            )
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
            while event:=sec.events.get():
                self._events.get_into(event)
        return self._events