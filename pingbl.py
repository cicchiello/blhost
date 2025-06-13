#!env python3

import serial
import time

# Configure this for your COM port and baud rate
#PORT = "COM3"
#PORT = "/dev/ttyACM0"
PORT = "/dev/tty.usbmodem14203"
BAUDRATE = 115200
TIMEOUT = 2  # seconds


def ping_bootloader():
    try:
        print("TRACE: openning port: %s" % PORT)
        print("TRACE: baud: %s" % BAUDRATE)
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            print(f"Opened {PORT} at {BAUDRATE} baud")

            # Flush input/output buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

#            while True:
#                c = ser.read(1)
#                print("INFO: c: %d" % c[0])
                
            # Send SYNC byte (0x7F)
            ser.write(b'\x7F')
            print("Sent 0x7F (sync byte)")

            # Wait for ACK (0x79) or NACK (0x1F)
            response = ser.read(1)
            if response == b'\x79':
                print("INFO: Received ACK (0x79) — bootloader is active!")
                ser.write(b'\x00')
                ser.write(b'\xFF')
                
                r0 = ser.read(17)
                print(f"TRACE: after read 0: {r0.hex()}")
                r1 = ser.read(1)
                print(f"TRACE: after read 1: {r1.hex()}")
                r2 = ser.read(1)
                print(f"TRACE: after read 2: {r2.hex()}")
                r3 = ser.read(1)
                print(f"TRACE: after read 3: {r3.hex()}")
                r4 = ser.read(1)
                print(f"TRACE: after read 4: {r4.hex()}")
                r5 = ser.read(1)
                print(f"TRACE: after read 5: {r5.hex()}")
                r6 = ser.read(1)
                print(f"TRACE: after read 6: {r6.hex()}")
                r7 = ser.read(1)
                print(f"TRACE: after read 7: {r7.hex()}")
                print(f"INFO: response to 0x00: {r0.hex()}{r1.hex()}{r2.hex()}{r3.hex()}{r4.hex()}{r5.hex()}{r6.hex()}{r7.hex()}")
                
            elif response == b'\x1F':
                print("WARNING: Received NACK (0x1F) — device rejected command")
            elif response == b'':
                print("ERROR: No response — check wiring, boot mode, or baud rate")
            else:
                print(f"ERROR:  Received unexpected byte: {response.hex()}")

            ser.close()

    except serial.SerialException as e:
        print(f"Error opening serial port {PORT}: {e}")

if __name__ == "__main__":
    ping_bootloader()
