import time


class BluetoothController:
    def __init__(
        self,
        enabled,
        port,
        baudrate,
        timeout=1.0,
        write_timeout=2.0,
        startup_delay=2.0,
        retry_seconds=1.0,
        stop_command="S",
        go_command="G",
    ):
        self.enabled = enabled
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.startup_delay = startup_delay
        self.retry_seconds = retry_seconds
        self.stop_command = stop_command
        self.go_command = go_command
        self.serial = None
        self.last_command = None
        self.last_attempted_command = None
        self.last_attempted_at = 0.0
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
                rtscts=False,
                dsrdtr=False,
                xonxoff=False,
            )
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            print(f"Bluetooth connected on {self.port} at {self.baudrate} baud.")
            if self.startup_delay > 0:
                print(f"Waiting {self.startup_delay:.1f}s for Bluetooth serial link to settle...")
                time.sleep(self.startup_delay)
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

        now = time.time()
        if self.last_attempted_command == command and now - self.last_attempted_at < self.retry_seconds:
            return

        self.last_attempted_command = command
        self.last_attempted_at = now

        try:
            self.serial.write(command.encode("ascii"))
            self.last_command = command
            print(f"Bluetooth sent: {command}")
        except self.serial_module.SerialTimeoutException as exc:
            print(f"Bluetooth send timed out for {command}; will retry: {exc}")
        except (self.serial_module.SerialException, OSError) as exc:
            print(f"Bluetooth disabled: serial connection lost while sending {command}: {exc}")
            self.enabled = False

    def close(self):
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
