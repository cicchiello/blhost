

class bl_bin_dumper():
    def __init__(self, filename):
        self._f = open(filename, 'wb')
    
    def dump(self, thebyte):
        assert thebyte >= 0, "bl_bin_dumper.dump only accepts uint8_t values"
        assert thebyte < 256, "bl_bin_dumper.dump only accepts uint8_t values"
        self._f.write(bytes([thebyte]))

    def done(self):
        self._f.close()

    

