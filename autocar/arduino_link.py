"""Serial link to the Arduino, plus a non-actuating simulation link."""

import time
from typing import Optional

try:
    import serial
except ImportError:
    serial = None


class ArduinoCarLink:
    """Communicate with the Arduino sketch using newline-delimited text.

    Pi -> Arduino: C,<steering_degrees>,<throttle_0_to_255>
    Arduino -> Pi: S,<distance_cm> (S,-1 means an invalid sensor reading)
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        startup_delay_s: float = 2.0,
    ):
        if serial is None:
            raise RuntimeError(
                "pyserial is required for hardware mode; "
                "install it with `pip install pyserial`."
            )

        self._serial = serial.Serial(
            port,
            baudrate=baudrate,
            timeout=0,
            write_timeout=0.2,
        )
        self._rx_buffer = bytearray()
        self.distance_cm: Optional[float] = None
        self._distance_updated_at: Optional[float] = None

        # Opening a USB serial port may reset common Arduino boards.
        time.sleep(startup_delay_s)

    @property
    def distance_age_s(self) -> float:
        if self._distance_updated_at is None:
            return float("inf")
        return time.monotonic() - self._distance_updated_at

    def poll(self) -> None:
        available = self._serial.in_waiting
        if available:
            self._rx_buffer.extend(self._serial.read(min(available, 512)))

        while b"\n" in self._rx_buffer:
            raw_line, _, remainder = self._rx_buffer.partition(b"\n")
            self._rx_buffer = bytearray(remainder)

            try:
                text = raw_line.decode("ascii", errors="ignore").strip()
                fields = text.split(",")

                if len(fields) == 2 and fields[0] == "S":
                    value = float(fields[1])
                    self.distance_cm = value if value > 0 else None
                    self._distance_updated_at = time.monotonic()

            except (ValueError, UnicodeError):
                # Ignore malformed telemetry; stale-sensor checks can stop the car.
                continue

        # Prevent an incomplete/corrupt line from growing without bound.
        if len(self._rx_buffer) > 1024:
            self._rx_buffer.clear()

    def send_command(self, steering_deg: int, throttle: int) -> None:
        steering_deg = max(0, min(180, int(steering_deg)))
        throttle = max(0, min(255, int(throttle)))
        packet = f"C,{steering_deg},{throttle}\n".encode("ascii")
        self._serial.write(packet)

    def stop(self, steering_center_deg: int = 90) -> None:
        try:
            self.send_command(steering_center_deg, 0)
        except OSError:
            pass

    def close(self) -> None:
        self.stop()
        if self._serial.is_open:
            self._serial.close()


class SimulatedCarLink:
    """Dry-run link for checking camera/vision logic without moving a vehicle."""

    def __init__(self, simulated_distance_cm: float = 100.0):
        self.distance_cm: Optional[float] = simulated_distance_cm
        self._distance_updated_at = time.monotonic()
        self._last_print_at = 0.0

    @property
    def distance_age_s(self) -> float:
        return time.monotonic() - self._distance_updated_at

    def poll(self) -> None:
        self._distance_updated_at = time.monotonic()

    def send_command(self, steering_deg: int, throttle: int) -> None:
        now = time.monotonic()
        if now - self._last_print_at >= 1.0:
            print(
                f"[SIMULATION] steering={steering_deg:3d} deg, "
                f"throttle={throttle:3d}/255"
            )
            self._last_print_at = now

    def stop(self, steering_center_deg: int = 90) -> None:
        print("[SIMULATION] STOP")

    def close(self) -> None:
        self.stop()
