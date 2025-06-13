#!env python3

import serial
import time

# Configure this for your COM port and baud rate
#PORT = "COM3"
#PORT = "/dev/ttyACM0"
PORT = "/dev/tty.usbmodem14203"
BAUDRATE = 115200
TIMEOUT = 2  # seconds
INTRA_CH = 0.1 # delay after each ser.write(byte)


def send_cmd(ser, cmd):
    ser.write(bytes([cmd]))
    time.sleep(INTRA_CH)
    ser.write(bytes([cmd ^ 0xFF]))
    time.sleep(INTRA_CH)


def get_ack_resp(ser, expectedlen=1):
    response = ser.read(expectedlen)
    
    if len(response) >= 1 and response[0] == 0x79:
        return response
    
    if len(response) < 1:
        print("No data received")
    elif response[0] == 0x1F:
        print("NACK received")
    else:
        print(f"Unexpected first byte: 0x{response[0]:02X}")
    
    return None


def send_acknowledged_cmd(ser, cmd):
    send_cmd(ser, cmd)
    response = get_ack_resp(ser)
    if not response:
        return None
    # get_ack_resp already confirmed ACK
    return response


def bl_init(ser):
    # Flush input/output buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send SYNC byte (0x7F)
    ser.write(b'\x7F')
    #print("Sent 0x7F (sync byte)")
    
    # Wait for ACK (0x79) or NACK (0x1F)
    response = ser.read(1)
    return response if response == b'\x79' else None

    
def bl_get_cmd(ser):
    response = send_acknowledged_cmd(ser, 0x00)
    if not response:
        return None

    # The number of Bytes to be received (less 1 for ACK)
    response = ser.read(1)
    if len(response) < 1:
        print("Unexpected len of bytelen response")
        return None

    bytelen = response[0]
    print("TRACE: bytelen: %d" % bytelen)

    response = ser.read(1) # get version
    bl_version = response[0]
    
    response = ser.read(bytelen)
    #print(f"TRACE: second GET_CMD response: {response.hex()}")

#    bl_version = response[0]

    print("TRACE: bl_get_cmd; trace 4: %s" % response.hex())
    if response.hex() != '0001021121314463738292':
        print(f"ERROR: unexpected GET_CMD response: {response.hex()}")
        return None

    return get_ack_resp(ser)



def bl_read_memory(ser, address, sz):
    assert sz >= 1, "bl_read_memory can only read up to 256 bytes at a time"
    assert sz <= 256, "bl_read_memory can only read up to 256 bytes at a time"
    
    response = send_acknowledged_cmd(ser, 0x11)
    if not response:
        return None

    _b0 = (address >> 24) & 0xFF
    _b1 = (address >> 16) & 0xFF
    _b2 = (address >> 8) & 0xFF
    _b3 = (address >> 0) & 0xFF
    
    ser.write(bytes([_b0]))
    time.sleep(INTRA_CH)
#    time.sleep(0.1)
    ser.write(bytes([_b1]))
    time.sleep(INTRA_CH)
#    time.sleep(0.1)
    ser.write(bytes([_b2]))
    time.sleep(INTRA_CH)
#    time.sleep(0.1)
    ser.write(bytes([_b3]))
    time.sleep(INTRA_CH)
#    time.sleep(0.1)
    
    # checksum
    _b4 = _b0 ^ _b1 ^ _b2 ^ _b3
    
    ser.write(bytes([_b4]))
    time.sleep(INTRA_CH)
#    time.sleep(0.1)
    
    print("TRACE: sent address")

    response = get_ack_resp(ser)
    if not response:
        return None

    print("TRACE: got ACK")
    
    response = send_acknowledged_cmd(ser, sz-1)
    if not response:
        return None

    print("TRACE: got ACK: 0x%02x" % response[0])
    
    for _i in range(sz):
        print("TRACE: getting byte 0x%02x" % _i)
        _b = ser.read(1)
        time.sleep(INTRA_CH)
#        time.sleep(0.01)
        if len(_b) < 1:
            print("ERROR: bl_read_memory error")
            return None
        print("TRACE: got: 0x%02x" % _b[0])

    print("TRACE: done getting all bytes")
    return _b


    
if __name__ == "__main__":
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT,
                           parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE) as ser:
            print(f"Opened {PORT} at {BAUDRATE} baud")

            response = bl_init(ser)
            if response:
                print("INFO: Received ACK (0x79) — bootloader is active!")

                response = bl_get_cmd(ser)
                if not response:
                    exit()

                response = bl_read_memory(ser, 0x8005000, 256)
                if not response:
                    exit()
                    
                print(f"TRACE: got GET_CMD response: {response.hex()}")

            else:
                print(f"ERROR: failed to init")
        
    except serial.SerialException as e:
        print(f"Error opening serial port {PORT}: {e}")

