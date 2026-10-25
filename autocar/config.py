"""Central configuration for camera processing and vehicle behavior."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleConfig:
    # Camera
    camera_width: int = 640
    camera_height: int = 480
    roi_top_ratio: float = 0.52
    target_y_ratio: float = 0.78

    # Steering servo limits
    steering_center_deg: int = 90
    steering_min_deg: int = 55
    steering_max_deg: int = 125
    steering_sign: int = 1

    # Motion and safety
    cruise_throttle: int = 90
    min_obstacle_distance_cm: float = 25.0
    sensor_timeout_s: float = 0.6
    max_lane_error_for_motion: float = 0.98

    # PID output is a steering-angle correction in degrees.
    pid_kp: float = 28.0
    pid_ki: float = 0.0
    pid_kd: float = 3.5
    pid_max_correction_deg: float = 25.0
    pid_integral_limit: float = 1.0

    # Serial connection to the Arduino
    serial_baudrate: int = 115200
    serial_startup_delay_s: float = 2.0


DEFAULT_CONFIG = VehicleConfig()
