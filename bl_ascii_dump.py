

class bl_ascii_dumper():
    def __init__(self, start_address):
        self._start_address = start_address
        self._line = "%04x " % self._start_address
        self._asc = ""
        self._cnt = 0
    
    def dump(self, thebyte):
        self._cnt += 1
        self._line = "%s%02x" % (self._line, thebyte) if self._cnt % 2 == 1 else "%s%02x " % (self._line, thebyte)
        _char = chr(thebyte)
        self._asc = "%s%c" % (self._asc, _char if _char.isprintable() else '.')
        if (self._cnt % 16) == 0:
            print("INFO: %s %s" % (self._line, self._asc))
            self._line = "%04x " % (self._start_address + self._cnt)
            self._asc = ""

    def done(self):
        pass

