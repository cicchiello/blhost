
import serial

from blhost import bl_host
from bl_bin_dump import bl_bin_dumper
from bl_ascii_dump import bl_ascii_dumper

# Configure this for your serial port
#PORT = "COM3"
PORT = "/dev/ttyACM0"
#PORT = "/dev/tty.usbmodem14203"

BAUDRATE = 115200
ADDRESS = 0x08005000
READ_LEN_KB = 512-20


if __name__ == "__main__":
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=2,
                           parity=serial.PARITY_EVEN,
                           stopbits=serial.STOPBITS_ONE) as ser:
            print(f"Opened {PORT} at {BAUDRATE} baud")

            _host = bl_host(ser)
            if _host.is_valid():
                print("INFO: Received ACK (0x79) — bootloader is active!")

                response = _host.bl_get_cmd()
                if not response:
                    exit()

                    
                _dumper = bl_bin_dumper("./fw.bin")
                #_dumper = bl_ascii_dumper(ADDRESS)
                try:
                    
                    for _i in range(int(READ_LEN_KB*1024/256)):
                        if not _host.bl_read_memory(ADDRESS+_i*256, 256, _dumper):
                            break;

                    print("\nINFO: Done.")
                    
                finally:
                    _dumper.done()
                    
            else:
                print(f"ERROR: failed to init")
        
    except serial.SerialException as e:
        print(f"Error opening serial port {PORT}: {e}")

    
