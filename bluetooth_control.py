class BluetoothController:
    def __init__(
        self,
        enabled,
        port,
        baudrate,
        timeout=1.0,
        write_timeout=0.5,
        stop_command="S",
        go_command="G",
    ):
        self.enabled = enabled
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.stop_command = stop_command
        self.go_command = go_command
        self.serial = None
        self.last_command = None
        self.serial_module = None

        if not self.enabled:
            return

        try:
            import serial
        except ImportError:
            print("Bluetooth disabled: install pyserial with `pip install pyserial`.")
            self.enabled = False
            return

        self.serial_module = serial

        try:
            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
            )
            print(f"Bluetooth connected on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as exc:
            print(f"Bluetooth disabled: could not open {self.port}: {exc}")
            self.enabled = False

    def send_stop(self):
        self._send_once(self.stop_command)

    def send_go(self):
        self._send_once(self.go_command)

    def _send_once(self, command):
        if not self.enabled or self.serial is None or self.last_command == command:
            return

        try:
            self.serial.write(command.encode("ascii"))
            self.last_command = command
            print(f"Bluetooth sent: {command}")
        except (self.serial_module.SerialException, self.serial_module.SerialTimeoutException, OSError) as exc:
            print(f"Bluetooth disabled: could not send {command}: {exc}")
            self.enabled = False

    def close(self):
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
