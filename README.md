<p align="center">
  <img
    src="https://capsule-render.vercel.app/api?type=waving&color=0:141E30,50:243B55,100:3A6073&height=210&section=header&text=Autonomous%20Driving&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Computer%20Vision%20%7C%20PID%20Control%20%7C%20Hardware%20Integration&descAlignY=60&descSize=13"
    width="100%"
    alt="Autonomous Driving Project Banner"
  />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Raspberry%20Pi-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Raspberry Pi" />
  <img src="https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white" alt="Arduino" />
  <img src="https://img.shields.io/badge/License-MIT-3A6073?style=for-the-badge" alt="MIT License" />
</p>

<p align="center">
  <b>A physical autonomous vehicle prototype integrating computer vision, steering control, and embedded hardware.</b>
  <br />
  Built with Raspberry Pi, Arduino, OpenCV, and a PID controller.
</p>

<p align="center">
  <a href="#-key-features">Features</a> ·
  <a href="#-system-architecture">Architecture</a> ·
  <a href="#-getting-started">Getting Started</a> ·
  <a href="#-testing-and-validation">Testing</a>
</p>

---

## 🚗 Project Overview

This project integrates camera-based lane detection, PID steering control, ultrasonic obstacle detection, and serial communication to implement lane-following behavior on a physical vehicle.

The Raspberry Pi processes camera frames and calculates steering commands. An Arduino receives these commands and controls the steering servo and motor output while monitoring ultrasonic distance measurements.

The project focuses on connecting software components with physical hardware, including control logic, communication protocols, testing, and stop conditions.

## ✨ Key Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>👁️ Computer Vision</h3>
      <p>OpenCV-based lane detection using grayscale conversion, Gaussian blur, Canny edge detection, and probabilistic Hough line detection.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🎯 PID Steering Control</h3>
      <p>Calculates a normalized lane-center error and uses PID control to generate bounded steering corrections.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>📡 Hardware Communication</h3>
      <p>Exchanges steering commands, throttle values, and ultrasonic distance telemetry between the Raspberry Pi and Arduino over serial.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ Stop Conditions</h3>
      <p>Implements stop logic for nearby obstacles, invalid or stale sensor readings, lost lane detection, excessive lane error, and communication timeouts.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔧 Embedded Control</h3>
      <p>Uses Arduino firmware to control the steering servo, motor driver, and HC-SR04 ultrasonic sensor.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🧪 Testing & Simulation</h3>
      <p>Includes PID unit tests and a software simulation mode for examining the camera-processing and control pipeline without actuating the vehicle.</p>
    </td>
  </tr>
</table>

---

## 🧭 System Architecture

The system separates image processing and high-level control from low-level hardware control.

```mermaid
flowchart TD
    CAM["Camera"] --> PI["Raspberry Pi"]
    PI --> CV["OpenCV Lane Detection"]
    CV --> ERR["Lane-Center Error"]
    ERR --> PID["PID Steering Controller"]
    PID --> CMD["Serial Command<br/>C, steering, throttle"]
    CMD --> ARD["Arduino Firmware"]

    ARD --> SERVO["Steering Servo"]
    ARD --> MOTOR["L298N Motor Driver"]
    MOTOR --> VEHICLE["Vehicle Motion"]

    SONAR["HC-SR04 Ultrasonic Sensor"] --> ARD
    ARD --> TEL["Distance Telemetry<br/>S, distance_cm"]
    TEL --> PI

    style PI fill:#243B55,color:#ffffff,stroke:#3A6073
    style ARD fill:#243B55,color:#ffffff,stroke:#3A6073
    style PID fill:#176B67,color:#ffffff,stroke:#2D9C91
    style VEHICLE fill:#3A6073,color:#ffffff,stroke:#141E30
