import socket
import time


class BluetoothController:
    def __init__(
        self,
        enabled,
        host,
        port,
        timeout=5.0,
        reconnect_seconds=2.0,
        stop_command="S",
        go_command="G",
    ):
        self.enabled = enabled
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reconnect_seconds = reconnect_seconds
        self.stop_command = stop_command
        self.go_command = go_command
        self.sock = None
        self.last_command = None
        self.last_attempted_command = None
        self.last_attempted_at = 0.0

        if not self.enabled:
            return

        self._connect()

    def _connect(self):
        try:
            self.sock = socket.create_connection(
                (self.host, self.port),
                timeout=self.timeout,
            )
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print(f"TCP connected to {self.host}:{self.port}")
        except (socket.timeout, OSError) as exc:
            print(f"TCP disabled: could not connect to {self.host}:{self.port}: {exc}")
            self.enabled = False

    def send_stop(self):
        self._send_once(self.stop_command)

    def send_go(self):
        self._send_once(self.go_command)

    def _send_once(self, command):
        if not self.enabled or self.sock is None or self.last_command == command:
            return

        now = time.time()
        if self.last_attempted_command == command and now - self.last_attempted_at < self.reconnect_seconds:
            return

        self.last_attempted_command = command
        self.last_attempted_at = now

        try:
            self.sock.sendall(command.encode("ascii"))
            self.last_command = command
            print(f"TCP sent: {command}")
        except OSError as exc:
            print(f"TCP connection lost while sending {command}: {exc}")
            self._reconnect()

    def _reconnect(self):
        print(f"Reconnecting to {self.host}:{self.port} in {self.reconnect_seconds}s...")
        time.sleep(self.reconnect_seconds)
        self.sock = None
        self._connect()

    def close(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
