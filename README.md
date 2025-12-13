# AIRMAN – Embedded Telemetry & AHRS System
**Author:** Prajen  
**Role:** Embedded / Firmware Engineer – Technical Assessment  
**Repository Type:** Private (Access granted to reviewers)

---

## 📌 Overview

This repository contains my complete submission for the **AIRMAN Embedded Firmware Technical Assessment**, covering both **Level 1** and **Level 2** tasks.

The project demonstrates an **end-to-end embedded telemetry pipeline**, starting from sensor data generation and UART-style framing, and extending to **AHRS-based orientation estimation**, robust checksum handling, logging, and visualization.

The overall design mirrors a **real-world UAV / robotics firmware architecture**, emphasizing:
- Deterministic behavior
- Communication reliability
- Clean separation of responsibilities
- Ground-station style monitoring

---

## 🧭 Project Structure

AIRMAN/
│
├── level1/ # Core telemetry pipeline (sensor simulation + UART framing)
├── level2/ # AHRS computation + enhanced telemetry + visualization
└── README.md # This document

yaml
Copy code

Each level is **self-contained**, with its own source code, receiver scripts, and documentation.

---

## 🔹 Level 1 — Telemetry Pipeline (Core Firmware)

**Focus:**  
Building a reliable telemetry link using simulated sensor data.

**Key Concepts Demonstrated:**
- Sensor signal simulation (IMU, altitude, temperature)
- UART-style ASCII frame encoding
- XOR checksum generation & validation
- Deterministic timing (20 Hz)
- Python-based receiver & CSV logging

Level 1 establishes the **foundation of a telemetry system**, similar to early-stage firmware bring-up or hardware abstraction testing.

➡️ See `level1/README.md` for full details.

---

## 🔹 Level 2 — AHRS & Advanced Telemetry (Extension)

**Focus:**  
Adding orientation estimation and ground-station style visualization.

**Key Concepts Demonstrated:**
- Madgwick AHRS filter (sensor fusion)
- Quaternion-based orientation tracking
- Conversion to roll, pitch, and heading
- Enhanced telemetry protocol
- CRC16-CCITT checksum for robust error detection
- Real-time visualization & flight-style monitoring
- Structured logging for offline analysis

Level 2 reflects **production-style embedded thinking**, where estimation, communication, and observability are treated as a complete system.

➡️ See `level2/README.md` for full details.

---

## 🧠 Design Philosophy

This project was designed with the following principles:

- **Clarity over cleverness**  
  Code is readable, well-commented, and intentionally structured.

- **Deterministic behavior**  
  Fixed update rates and predictable execution paths.

- **Real-world resemblance**  
  Architecture mirrors how embedded telemetry and AHRS systems are actually built.

- **Progressive complexity**  
  Level 1 → data transport  
  Level 2 → estimation + monitoring

---

## 🤖 Use of AI Tools

AI tools (ChatGPT) were used responsibly as **engineering assistance**, similar to:
- Consulting documentation
- Reviewing algorithms
- Refining code structure
- Improving documentation clarity

All code was:
- Written by me
- Tested by me
- Fully understood by me

No code was blindly copied or used without comprehension.

---

## 📝 Notes for Reviewers

- Both levels strictly follow the assessment specification.
- Each folder contains a dedicated README explaining implementation details.
- The repository is private; reviewer access has been explicitly granted.
- The focus is on **embedded fundamentals, correctness, and system thinking**, not UI polish.

---

## 🚀 Submission Status

✅ **Level 1: Complete**  
✅ **Level 2: Complete**  

The repository represents a full, working embedded telemetry and AHRS system suitable for evaluation in an internship or junior firmware engineering role.

---

Thank you for reviewing my submission.
