import argparse
import time

import serial
import serial.tools.list_ports


def list_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return

    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")


def send_command(port, baudrate, command):
    print(f"Opening {port} at {baudrate} baud...")

    with serial.Serial(
        port,
        baudrate,
        timeout=1,
        write_timeout=5,
        rtscts=False,
        dsrdtr=False,
        xonxoff=False,
    ) as bt:
        bt.reset_input_buffer()
        bt.reset_output_buffer()

        print("Waiting for Bluetooth serial link...")
        time.sleep(2)

        print(f"Sending {command!r}...")
        written = bt.write(command.encode("ascii"))
        print(f"Sent {written} byte(s).")


def main():
    parser = argparse.ArgumentParser(description="Test HC-05 Bluetooth serial commands.")
    parser.add_argument("--list", action="store_true", help="List available serial ports.")
    parser.add_argument("--port", default="COM7", help="Bluetooth COM port, for example COM7.")
    parser.add_argument("--baudrate", type=int, default=9600, help="Bluetooth baud rate.")
    parser.add_argument("--send", default="G", help="Single command to send, for example G or S.")
    args = parser.parse_args()

    if args.list:
        list_ports()
        return

    if len(args.send) != 1:
        raise ValueError("--send must be exactly one character, for example G or S.")

    send_command(args.port, args.baudrate, args.send)


if __name__ == "__main__":
    main()
