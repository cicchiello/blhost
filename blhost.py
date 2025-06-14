
import serial

from bl_ascii_dump import bl_ascii_dumper


class bl_host():

    def __init__(self, ser):
        self._ser = ser
        self._valid = self.bl_init()

    def is_valid(self):
        return self._valid
    
    def bl_init(self):
        # Flush input/output buffers
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        
        # Send SYNC byte (0x7F)
        self._ser.write(b'\x7F')
        
        # Wait for ACK (0x79) or NACK (0x1F)
        self._valid = self._ser.read(1) == b'\x79'
        return self._valid

    
    def bl_get_cmd(self):
        self._valid = self._send_acknowledged_cmd(0x00)
        if not self._valid:
            return None

        # The number of Bytes to be received (less 1 for ACK)
        response = self._ser.read(1)
        if len(response) < 1:
            print("Unexpected len of bytelen response")
            self._valid = False
            return None
        
        bytelen = response[0]
        
        response = self._ser.read(1) # get version
        bl_version = response[0]
        
        response = self._ser.read(bytelen)
        
        if response.hex() != '0001021121314463738292':
            print(f"ERROR: unexpected GET_CMD response: {response.hex()}")
            self._valid = False
            return None
    
        return self._get_ack_resp()


    def bl_read_memory(self, address, sz, dumper=None):
        assert sz >= 1, "bl_read_memory can only read up to 256 bytes at a time"
        assert sz <= 256, "bl_read_memory can only read up to 256 bytes at a time"
        
        self._valid = self._send_acknowledged_cmd(0x11)
        if not self._valid:
            return None
        
        _b0 = (address >> 24) & 0xFF
        _b1 = (address >> 16) & 0xFF
        _b2 = (address >> 8) & 0xFF
        _b3 = (address >> 0) & 0xFF
        
        # checksum
        _b4 = _b0 ^ _b1 ^ _b2 ^ _b3
        
        self._ser.write(bytes([_b0, _b1, _b2, _b3, _b4]))
        
        self._valid = self._get_ack_resp()
        if not self._valid:
            return None
        
        self._valid = self._send_acknowledged_cmd(sz-1)
        if not self._valid:
            return None

        if dumper is None:
            dumper = bl_ascii_dumper(address)

        for _i in range(sz):
            _b = self._ser.read(1)
            if len(_b) < 1:
                print("ERROR: bl_read_memory error")
                self._valid = False
                return None
            dumper.dump(_b[0])
            
        return _b


    def _send_cmd(self, cmd):
        self._ser.write(bytes([cmd, cmd ^ 0xFF]))

        
    def _get_ack_resp(self, expectedlen=1):
        response = self._ser.read(expectedlen)
    
        self._valid = len(response) >= 1 and response[0] == 0x79
        if self._valid:
            return self._valid

        if len(response) < 1:
            print("No data received")
        elif response[0] == 0x1F:
            print("NACK received")
        else:
            print(f"Unexpected first byte: 0x{response[0]:02X}")
    
        return False

    
    def _send_acknowledged_cmd(self, cmd):
        self._send_cmd(cmd)
        return self._get_ack_resp()



