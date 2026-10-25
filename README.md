# Autonomous Driving System

A Raspberry Pi and Arduino-based autonomous driving prototype that combines camera-based lane detection, PID steering control, ultrasonic obstacle detection, and serial communication.

## Overview

This project integrates computer vision and embedded control to implement lane-following behavior on a physical vehicle platform.

The Raspberry Pi processes camera frames to detect lane boundaries and calculates steering corrections using a PID controller. It communicates with an Arduino over serial, while the Arduino handles steering servo control, motor output, and ultrasonic distance monitoring.

## Features

- **Lane Detection:** Uses OpenCV image processing, Canny edge detection, and probabilistic Hough line detection to identify lane boundaries.
- **PID Steering Control:** Calculates steering corrections from the detected lane-center offset.
- **Obstacle Detection:** Uses an HC-SR04 ultrasonic sensor to measure distance ahead of the vehicle.
- **Arduino Motor Control:** Controls motor output through an L298N motor driver.
- **Serial Communication:** Exchanges steering, throttle, and distance data between the Raspberry Pi and Arduino.
- **Safety Stop Logic:** Stops motor output when an obstacle is too close, sensor readings are invalid or stale, lane detection is lost, or commands time out.
- **Unit Testing:** Includes tests for PID output direction, output clamping, and controller reset behavior.
- **Simulation Mode:** Supports a software simulation mode for checking the camera-processing and control pipeline without actuating the vehicle.

## System Architecture

```text
Camera
  |
  v
Raspberry Pi
  |
  +--> OpenCV Lane Detection
  |         |
  |         v
  |     Lane Position Error
  |         |
  |         v
  |      PID Control
  |         |
  |         v
  +---- Serial Commands --------+
                                |
                                v
                             Arduino
                                |
                 +--------------+--------------+
                 |              |              |
                 v              v              v
             Servo Motor    Motor Driver   Ultrasonic
                               (L298N)       Sensor
                 |              |              |
                 v              v              |
              Steering       Vehicle Motion    |
                                                |
                         Distance Telemetry <---+
                                |
                                v
                           Raspberry Pi
```

## Hardware Components

The following components are referenced by the current source code. Confirm that the list matches the hardware used in your physical tests.

| Component | Purpose |
|---|---|
| Raspberry Pi | Image processing and high-level control |
| Arduino board | Motor, steering, and sensor control |
| Camera | Captures images for lane detection |
| HC-SR04 ultrasonic sensor | Measures obstacle distance |
| L298N motor driver | Drives the vehicle motors |
| Steering servo | Adjusts steering direction |
| Vehicle chassis and motors | Physical vehicle platform |

## Software Requirements

- Python 3.9 or later
- NumPy
- OpenCV
- pySerial
- Arduino IDE or a compatible Arduino build environment

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```text
Autonomous-driving/
├── README.md
├── main.py
├── requirements.txt
├── autocar/
│   ├── __init__.py
│   ├── config.py
│   ├── pid.py
│   ├── lane_detector.py
│   └── arduino_link.py
├── arduino/
│   └── autonomous_car/
│       └── autonomous_car.ino
└── tests/
    └── test_pid.py
```

## Configuration

Control parameters are centralized in `autocar/config.py`, including:

- Camera resolution and region of interest
- Steering center and angle limits
- Cruise throttle
- Minimum obstacle distance
- Sensor timeout
- PID gains and output limits
- Serial baud rate and startup delay

Review the configuration against the actual hardware before operating the vehicle. Steering direction, servo limits, and motor behavior may vary between chassis.

## Serial Communication Protocol

The Raspberry Pi and Arduino communicate using newline-delimited ASCII messages at 115200 baud.

### Raspberry Pi to Arduino

```text
C,<steering_degrees>,<throttle>
```

Example:

```text
C,90,100
```

The fields represent the requested steering angle and throttle value.

### Arduino to Raspberry Pi

```text
S,<distance_cm>
```

Example:

```text
S,42.5
```

An invalid ultrasonic reading is reported as:

```text
S,-1
```

The Arduino independently checks command freshness and ultrasonic readings before enabling motor output.

## Running the Application

### 1. Simulation Mode

To run without connecting to the Arduino or sending motor commands:

```bash
python main.py --simulate --camera 0
```

Replace `0` with the appropriate camera index if necessary.

Simulation mode still uses the camera-processing pipeline. It does not simulate the full physical vehicle dynamics or prove that the vehicle can follow lanes successfully.

### 2. Hardware Mode

Connect the camera and Arduino, verify the serial port, and review all hardware settings before running:

```bash
python main.py --port /dev/ttyACM0 --camera 0
```

On Windows, the Arduino port may look like `COM3`. Use the port assigned to your device.

For headless operation without the OpenCV preview window:

```bash
python main.py --port /dev/ttyACM0 --camera 0 --headless
```

**Safety:** Perform initial motor tests with the drive wheels lifted, keep a physical power disconnect within reach, and verify the emergency stopping behavior before driving the vehicle on the ground.

## Testing

Run the available PID unit tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

The current PID tests cover:

- Expected output sign for positive and negative errors
- Output clamping at configured limits
- Resetting the controller's derivative history

These tests cover selected software behavior only. They do not constitute a complete hardware integration or vehicle performance test.

## Hardware Integration and Validation

The project was integrated with a physical vehicle platform. The reported verification activities include Arduino firmware execution, serial communication between the connected components, and physical lane-following tests.

The lane-following result applies to the hardware configuration and test conditions used during testing. It does not establish reliable performance under all lighting conditions, lane markings, surfaces, speeds, or environments.

The software includes stop conditions for obstacles, invalid or stale sensor readings, and loss of lane detection. These mechanisms should not be interpreted as a guarantee of safety under every possible hardware failure.

For reproducibility, record the actual hardware configuration, wiring, software versions, test conditions, and observed results. Report only tests that were performed and results that were observed.

## Limitations and Future Improvements

Potential areas for further development include:

- More robust lane detection under varying lighting and lane-marking conditions
- Improved handling of partial or missing lane boundaries
- Additional unit and integration tests
- Logging of steering commands, sensor measurements, and stop events
- Quantitative evaluation of lane-following performance
- More comprehensive fault handling and hardware safety validation
