# AIRMAN – Level 2 AHRS Telemetry System

**Author:** Prajen
**Role:** Embedded intern – Technical Assessment (Level 2)
**Submission:** AHRS computation + enhanced telemetry + real-time visualization

---

## 📌 Overview

This project implements the **Level-2 Advanced Extension** of the AIRMAN firmware assessment.

It builds on a telemetry pipeline by adding a **full Attitude and Heading Reference System (AHRS)**, enhanced telemetry framing, robust checksum validation, and real-time visualization.

The system closely resembles a **real embedded flight-control / robotics telemetry stack**, covering:
- Sensor fusion
- Orientation estimation
- Communication robustness
- Ground-station style visualization and logging

---

## ✔ Features Implemented

### **1. AHRS Algorithm (C – Madgwick Filter)**

A **Madgwick AHRS filter** is implemented to estimate orientation using:
- Accelerometer
- Gyroscope
- Magnetometer



**Outputs:**
- Roll (deg)
- Pitch (deg)
- Heading / Yaw (deg)

Key characteristics:
- Quaternion-based orientation tracking
- Continuous normalization for numerical stability
- Suitable for real-time embedded execution
- Widely used in UAVs, robotics, and IMU systems

This satisfies the Level-2 requirement for a **recommended AHRS algorithm**.

---

### **2. Enhanced Level-2 Telemetry Protocol**

Telemetry frames are transmitted at **20 Hz (50 ms)** in the following format:

`$L2,<timestamp_ms>,<roll>,<pitch>,<heading>,<alt>,<temp>*<CHK>`

Where:
- `$` → Start of frame
- `*` → Start of checksum
- `<CHK>` → **CRC16-CCITT checksum**

Compared to Level-1:
- XOR checksum is replaced with **CRC16** for stronger error detection
- Payload carries **AHRS outputs** instead of raw IMU values

This mirrors real-world embedded telemetry protocols used in aerospace and robotics.

---

### **3. Real-Time Visualization & Logging (Python)**

A Python-based receiver performs:
- Frame reception via **STDIN (pipe mode)**
- **CRC16 checksum validation**
- Parsing of AHRS telemetry
- Deterministic logging into **CSV**
- Real-time plotting (≥10 Hz) using Python visualization tools

The receiver behaves like a **lightweight Ground Control Station (GCS)** used during system integration and testing.

---

## 📁 File Structure

```
level1/
│
├── ahrs_filter.c         # C source for telemetry generator
├── plot_live.py          # Python receiver script
├── dash.py               #dashboard
├── output.csv            # Generated during execution
└── README.md             # Documentation (this file)
```

---


## 📈 Performance

- **Telemetry rate:** 20 Hz (exceeds ≥10 Hz requirement)  
- **AHRS stability:** Smooth roll, pitch, and heading outputs  
- **Checksum robustness:** CRC16 reliably detects corrupted frames  
- **Logging:** Deterministic CSV output suitable for offline analysis  
- **Visualization:** Continuous real-time attitude monitoring  

The system runs stably for extended durations without numerical drift or frame loss.

---

## ⚠️ Limitations

- **Simulated sensors:** IMU data is simulated; no real sensor calibration applied  
- **Simplified motion model:** Smooth, predictable motion patterns only  
- **Single-threaded transmitter:** Chosen for determinism and clarity  
- **No control loop:** Estimation only; no actuation or feedback control  

These limitations were intentional to keep the focus on **AHRS correctness, protocol design, and system clarity**, as required by Level-2.

---

## 🤖 AI Tools Used

AI tools (ChatGPT) were used responsibly as engineering assistance, similar to consulting documentation or a senior engineer.

AI support was used for:
- Reviewing AHRS concepts and quaternion math  
- Verifying CRC16 checksum logic  
- Improving code structure and comments  
- Refining documentation clarity and professionalism  

All code was **written, tested, and fully understood by me**.  
No code was blindly copied or used without comprehension.

---

## 📝 Notes for Reviewers (AIRMAN Team)

- Madgwick filter selected as the **recommended AHRS algorithm**  
- Telemetry protocol strictly follows Level-2 specification  
- CRC16 improves communication reliability over Level-1  
- Design emphasizes clarity, modularity, and real-world firmware style  
- Visualization and logging mirror real ground-station workflows  

---

## 🚀 Final Status

**Level 2 implementation: COMPLETE**  
AHRS computation, enhanced telemetry protocol, logging, and real-time visualization are fully implemented and functional.
