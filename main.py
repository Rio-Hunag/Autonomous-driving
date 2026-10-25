import argparse
import sys
import time

import cv2

from autocar.arduino_link import ArduinoCarLink, SimulatedCarLink
from autocar.config import DEFAULT_CONFIG
from autocar.lane_detector import LaneDetector
from autocar.pid import PIDController


def parse_args():
    parser = argparse.ArgumentParser(
        description="Autonomous-driving lane-following system"
    )
    parser.add_argument(
        "--port",
        default="/dev/ttyACM0",
        help="Arduino serial port, e.g. /dev/ttyACM0 or COM3",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="OpenCV camera index (default: 0)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Do not connect to or actuate hardware; print commands only",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Do not open an OpenCV preview window",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = DEFAULT_CONFIG

    if args.simulate:
        link = SimulatedCarLink()
    else:
        try:
            link = ArduinoCarLink(
                args.port,
                baudrate=cfg.serial_baudrate,
                startup_delay_s=cfg.serial_startup_delay_s,
            )
        except Exception as exc:
            print(
                f"Could not open Arduino serial port {args.port!r}: {exc}",
                file=sys.stderr,
            )
            print(
                "Check the USB cable and serial port, or use --simulate "
                "to test the camera-processing pipeline without motor actuation.",
                file=sys.stderr,
            )
            return 2

    camera = cv2.VideoCapture(args.camera)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.camera_width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.camera_height)

    if not camera.isOpened():
        print(
            f"Could not open camera index {args.camera}.",
            file=sys.stderr,
        )
        link.close()
        return 2

    detector = LaneDetector(
        cfg.roi_top_ratio,
        cfg.target_y_ratio,
    )

    pid = PIDController(
        cfg.pid_kp,
        cfg.pid_ki,
        cfg.pid_kd,
        output_limits=(
            -cfg.pid_max_correction_deg,
            cfg.pid_max_correction_deg,
        ),
        integral_limit=cfg.pid_integral_limit,
    )

    previous_time = time.monotonic()

    print("Starting. Press q or ESC in the preview window to stop.")
    print(
        "Use a raised test stand first; keep a physical power disconnect "
        "within reach."
    )

    try:
        while True:
            link.poll()

            ok, frame = camera.read()
            if not ok or frame is None:
                print("Camera frame unavailable; stopping.", file=sys.stderr)
                link.stop(cfg.steering_center_deg)
                break

            now = time.monotonic()
            dt = max(1e-3, now - previous_time)
            previous_time = now

            detection = detector.detect(frame)

            distance = link.distance_cm
            sensor_fresh = link.distance_age_s <= cfg.sensor_timeout_s

            distance_safe = (
                distance is not None
                and sensor_fresh
                and cfg.min_obstacle_distance_cm <= distance <= 400.0
            )

            steering = cfg.steering_center_deg
            throttle = 0

            if (
                not sensor_fresh
                or distance is None
                or not (0 < distance <= 400.0)
            ):
                status = "SENSOR FAIL - STOP"
                pid.reset()

            elif distance < cfg.min_obstacle_distance_cm:
                status = "OBSTACLE - STOP"
                pid.reset()

            elif not detection.found:
                status = "LANE LOST - STOP"
                pid.reset()

            elif abs(detection.error_norm) > cfg.max_lane_error_for_motion:
                status = "LANE ERROR - STOP"
                pid.reset()

            else:
                correction = pid.update(detection.error_norm, dt)

                steering = round(
                    cfg.steering_center_deg
                    + cfg.steering_sign * correction
                )

                steering = max(
                    cfg.steering_min_deg,
                    min(cfg.steering_max_deg, steering),
                )

                turn_factor = max(
                    0.35,
                    1.0 - 0.65 * abs(detection.error_norm),
                )

                throttle = round(cfg.cruise_throttle * turn_factor)
                status = "RUN"

            # Arduino independently enforces obstacle and command-timeout stops.
            safe_throttle = (
                throttle
                if distance_safe and detection.found
                else 0
            )

            link.send_command(steering, safe_throttle)

            if not args.headless:
                shown = detection.debug_frame

                distance_text = (
                    "n/a"
                    if distance is None
                    else f"{distance:.1f} cm"
                )

                cv2.putText(
                    shown,
                    f"status: {status}",
                    (12, 58),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    shown,
                    f"ultrasonic: {distance_text}",
                    (12, 86),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                cv2.imshow(
                    "Autonomous Driving - press q to quit",
                    shown,
                )

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break

    except KeyboardInterrupt:
        print("\nInterrupted; stopping vehicle.")

    finally:
        try:
            link.stop(cfg.steering_center_deg)
            link.close()
        finally:
            camera.release()

            if not args.headless:
                cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
