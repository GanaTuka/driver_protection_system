import argparse
import socket


def send_command(host, port, command):
    print(f"Connecting to {host}:{port}...")

    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (socket.timeout, OSError) as exc:
        print(f"Connection failed: {exc}")
        return

    print(f"Sending {command!r}...")
    sent = sock.sendall(command.encode("ascii"))
    print(f"Sent {len(command)} byte(s).")
    sock.close()


def main():
    parser = argparse.ArgumentParser(description="Test TCP -> Phone -> Bluetooth command relay.")
    parser.add_argument("--host", default="192.168.1.100", help="Phone TCP server IP address.")
    parser.add_argument("--port", type=int, default=8080, help="Phone TCP server port.")
    parser.add_argument("--send", default="G", help="Single command to send, for example G or S.")
    args = parser.parse_args()

    if len(args.send) != 1:
        raise ValueError("--send must be exactly one character, for example G or S.")

    send_command(args.host, args.port, args.send)


if __name__ == "__main__":
    main()
