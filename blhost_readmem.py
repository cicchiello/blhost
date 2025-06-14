
import serial

from blhost import bl_host


# Configure this for your COM port and baud rate
#PORT = "COM3"
PORT = "/dev/ttyACM0"
#PORT = "/dev/tty.usbmodem14203"
BAUDRATE = 115200
TIMEOUT = 2  # seconds


if __name__ == "__main__":
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT,
                                  parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as ser:
            print(f"Opened {PORT} at {BAUDRATE} baud")

            _host = bl_host(ser)
            if _host.is_valid():
                print("INFO: Received ACK (0x79) — bootloader is active!")

                response = _host.bl_get_cmd()
                if not response:
                    exit()

                response = _host.bl_read_memory(0x8005000, 256)
                if not response:
                    exit()
                    
            else:
                print(f"ERROR: failed to init")
        
    except serial.SerialException as e:
        print(f"Error opening serial port {PORT}: {e}")

    
