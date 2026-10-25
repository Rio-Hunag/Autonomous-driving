"""Small PID controller with output and integral clamping."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class PIDController:
    kp: float
    ki: float
    kd: float
    output_limits: Tuple[float, float] = (-25.0, 25.0)
    integral_limit: float = 1.0

    def __post_init__(self) -> None:
        low, high = self.output_limits
        if low > high:
            raise ValueError("output_limits must be (minimum, maximum)")
        self._integral = 0.0
        self._previous_error: Optional[float] = None

    def reset(self) -> None:
        """Clear controller history, for example after losing lane detection."""
        self._integral = 0.0
        self._previous_error = None

    def update(self, error: float, dt: float) -> float:
        """Return a bounded control output for the supplied error and time step."""
        if dt <= 0:
            dt = 1e-3

        self._integral += error * dt
        self._integral = max(
            -self.integral_limit, min(self.integral_limit, self._integral)
        )

        if self._previous_error is None:
            derivative = 0.0
        else:
            derivative = (error - self._previous_error) / dt

        output = (
            self.kp * error
            + self.ki * self._integral
            + self.kd * derivative
        )

        low, high = self.output_limits
        output = max(low, min(high, output))
        self._previous_error = error
        return output
