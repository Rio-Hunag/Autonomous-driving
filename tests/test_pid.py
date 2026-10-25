import unittest

from autocar.pid import PIDController


class PIDControllerTests(unittest.TestCase):
    def test_output_has_expected_sign(self):
        controller = PIDController(
            kp=10.0,
            ki=0.0,
            kd=0.0,
            output_limits=(-20, 20),
        )

        self.assertGreater(controller.update(0.5, 0.1), 0)

        controller.reset()

        self.assertLess(controller.update(-0.5, 0.1), 0)

    def test_output_is_clamped(self):
        controller = PIDController(
            kp=100.0,
            ki=0.0,
            kd=0.0,
            output_limits=(-15, 15),
        )

        self.assertEqual(controller.update(1.0, 0.1), 15)
        self.assertEqual(controller.update(-1.0, 0.1), -15)

    def test_reset_clears_derivative_history(self):
        controller = PIDController(
            kp=0.0,
            ki=0.0,
            kd=1.0,
            output_limits=(-100, 100),
        )

        controller.update(0.0, 0.1)
        self.assertNotEqual(controller.update(1.0, 0.1), 0.0)

        controller.reset()

        self.assertEqual(controller.update(1.0, 0.1), 0.0)


if __name__ == "__main__":
    unittest.main()
