<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:141E30,50:243B55,100:3A6073&height=190&section=header&text=Autonomous%20Driving&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Computer%20Vision%20%7C%20PID%20Control%20%7C%20Hardware%20Integration&descAlignY=60&descSize=13" width="100%" alt="Autonomous Driving Project Banner"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/Raspberry%20Pi-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Raspberry Pi"/>
  <img src="https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white" alt="Arduino"/>
</p>

<h2 align="center">🚗 Autonomous Driving Prototype</h2>

<p align="center">
  A physical vehicle project combining lane detection, PID steering control,
  ultrasonic obstacle detection, and Raspberry Pi–Arduino communication.
</p>

---

## ✨ Project Overview

This project integrates computer vision and hardware control to implement lane-following behavior on a physical vehicle.

The Raspberry Pi processes camera frames, detects lane boundaries, and calculates steering corrections. An Arduino receives control commands and manages the steering servo, motor driver, and ultrasonic sensor.

The project focuses on practical software implementation, hardware integration, serial communication, and testing.

## ⚡ Key Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>👁️ Lane Detection</h3>
      OpenCV image processing with Canny edge detection and Hough line detection.
    </td>
    <td width="50%" valign="top">
      <h3>🎯 PID Steering</h3>
      Calculates steering corrections from the detected lane-center error.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>📡 Hardware Communication</h3>
      Exchanges steering commands and sensor telemetry between Raspberry Pi and Arduino.
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ Obstacle Detection</h3>
      Uses an HC-SR04 ultrasonic sensor and configured stop conditions.
    </td>
  </tr>
</table>

## 🧭 System Architecture

```mermaid
flowchart TD
    A["Camera"] --> B["Raspberry Pi"]
    B --> C["OpenCV Lane Detection"]
    C --> D["Lane-Center Error"]
    D --> E["PID Steering Controller"]
    E --> F["Serial Commands"]
    F --> G["Arduino"]
    G --> H["Steering Servo"]
    G --> I["L298N Motor Driver"]
    G --> J["HC-SR04 Sensor"]
    I --> K["Vehicle Motion"]
    J --> L["Distance Telemetry"]
    L --> B
