
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass
class LaneDetection:
    lane_center_x: Optional[float]
    error_norm: Optional[float]
    confidence: float
    debug_frame: np.ndarray

    @property
    def found(self) -> bool:
        return self.error_norm is not None


class LaneDetector:
    def __init__(self, roi_top_ratio: float = 0.52, target_y_ratio: float = 0.78):
        if not 0.0 < roi_top_ratio < 1.0:
            raise ValueError("roi_top_ratio must be between 0 and 1")
        if not 0.0 < target_y_ratio < 1.0:
            raise ValueError("target_y_ratio must be between 0 and 1")
        self.roi_top_ratio = roi_top_ratio
        self.target_y_ratio = target_y_ratio

    @staticmethod
    def _weighted_mean(items):
        total_weight = sum(weight for _, weight in items)
        if total_weight <= 0:
            return None
        return sum(value * weight for value, weight in items) / total_weight

    def detect(self, frame: np.ndarray) -> LaneDetection:
        if frame is None or frame.size == 0:
            raise ValueError("frame must be a non-empty image")

        height, width = frame.shape[:2]
        target_y = int(height * self.target_y_ratio)
        roi_top = int(height * self.roi_top_ratio)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 55, 150)

        mask = np.zeros_like(edges)
        polygon = np.array(
            [[
                (int(width * 0.04), height - 1),
                (int(width * 0.28), roi_top),
                (int(width * 0.72), roi_top),
                (int(width * 0.96), height - 1),
            ]],
            dtype=np.int32,
        )
        cv2.fillPoly(mask, polygon, 255)
        roi_edges = cv2.bitwise_and(edges, mask)

        lines = cv2.HoughLinesP(
            roi_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=22,
            minLineLength=max(20, int(width * 0.045)),
            maxLineGap=max(20, int(width * 0.06)),
        )

        left_candidates = []
        right_candidates = []
        rendered = frame.copy()

        if lines is not None:
            for line in lines[:, 0, :]:
                x1, y1, x2, y2 = (int(v) for v in line)
                dx = x2 - x1
                dy = y2 - y1

                if abs(dx) < 2:
                    continue

                slope = dy / float(dx)
                if abs(slope) < 0.40:
                    continue

                x_at_target = x1 + (target_y - y1) / slope
                if not (-0.2 * width <= x_at_target <= 1.2 * width):
                    continue

                length = float(np.hypot(dx, dy))

                if slope < 0 and x_at_target < width * 0.62:
                    left_candidates.append((x_at_target, length))
                    cv2.line(
                        rendered, (x1, y1), (x2, y2), (255, 160, 0), 2
                    )
                elif slope > 0 and x_at_target > width * 0.38:
                    right_candidates.append((x_at_target, length))
                    cv2.line(
                        rendered, (x1, y1), (x2, y2), (0, 180, 255), 2
                    )

        left_x = self._weighted_mean(left_candidates)
        right_x = self._weighted_mean(right_candidates)
        lane_center = None
        error_norm = None
        confidence = 0.0

        # Require both sides to avoid steering based on a single ambiguous edge.
        if left_x is not None and right_x is not None and left_x < right_x:
            lane_width = right_x - left_x
            if 0.15 * width <= lane_width <= 0.95 * width:
                lane_center = (left_x + right_x) / 2.0
                error_norm = (lane_center - width / 2.0) / (width / 2.0)

                total_line_length = sum(
                    weight for _, weight in left_candidates + right_candidates
                )
                confidence = min(1.0, total_line_length / (height * 1.4))

                cv2.circle(
                    rendered,
                    (int(lane_center), target_y),
                    7,
                    (0, 255, 0),
                    -1,
                )

        cv2.line(
            rendered,
            (width // 2, roi_top),
            (width // 2, height - 1),
            (200, 200, 200),
            1,
        )
        cv2.line(
            rendered,
            (0, target_y),
            (width - 1, target_y),
            (120, 120, 120),
            1,
        )

        if error_norm is None:
            label = "LANE LOST"
            color = (0, 0, 255)
        else:
            label = f"lane error: {error_norm:+.3f}"
            color = (0, 255, 0)

        cv2.putText(
            rendered,
            label,
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )

        return LaneDetection(lane_center, error_norm, confidence, rendered)
