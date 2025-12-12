# AIRMAN – Level 1 Telemetry Pipeline  
**Author:** Prajen  
**Role:** Embedded developer – Technical Assessment (Level 1)  
**Submission:** Telemetry generation + UART-style frame encoding + Python receiver

---

## 📌 Overview
This project implements a complete **Level-1 telemetry pipeline** as described in the AIRMAN firmware assessment.  

It includes:
- Simulated IMU sensor data (accelerometer, gyroscope)
- Simulated altitude and temperature signals
- UART-style telemetry framing at 20 Hz
- XOR checksum generation
- Python receiver that validates frames, parses data, and logs CSV output

The system replicates a simplified UAV/robotic telemetry link and demonstrates my understanding of embedded data generation, communication protocols, and receiver-side parsing.

---

## ✔ Features Implemented

### **1. Sensor Simulation (C)**
Simulated the following sensors:
- Accelerometer (ax, ay, az)
- Gyroscope (gx, gy, gz)
- Altitude
- Temperature

Each sensor model includes:
- Primary motion (sine/cosine functions)
- Drift
- Noise
- Realistic constraints (e.g., gravity on Z-axis, slow temp changes)

### **2. UART Frame Encoding**
Each frame is sent at **20 Hz (every 50 ms)** in the format:

```
$L1,<timestamp_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>,<alt>,<temp>*<CHK>
```

Where:
- `$` marks start of frame  
- `*` marks checksum start  
- `<CHK>` is XOR checksum of all bytes between `$` and `*`

### **3. Python Receiver**
The script performs:
- Frame input via STDIN (pipe mode)
- XOR checksum validation
- CSV logging into `output.csv`
- Human-readable console output
- Error detection for corrupted frames

---

## 📁 File Structure

```
level1/
│
├── telemetry_tx.c        # C source for telemetry generator
├── uart_rx.py            # Python receiver script
├── output.csv            # Generated during execution
└── README.md             # Documentation (this file)
```

---

## 🔧 How to Compile & Run

### **(A) Compile C Telemetry Generator**
Open **MSYS2 MINGW64** terminal:

```bash
gcc telemetry_tx.c -o telemetry_tx -lm
```

Run to test:

```bash
./telemetry_tx
```

---

### **(B) Run Full Telemetry System (Pipe Mode)**

Because UART hardware is optional in Level-1, frames are piped into Python:

```bash
./telemetry_tx | python uart_rx.py
```

If Python is installed at a specific Windows path:

```bash
./telemetry_tx | ./telemetry_tx | <python_path> uart_rx.py
```

This will:
- Validate each frame
- Print formatted output
- Write data into `output.csv`

---

## 🧠 Assumptions & Simplifications

1. **Simulated Data Instead of Real IMU Hardware**  
   Due to Level-1 allowing simulated data, physical IIO sensors were not required.

2. **20 Hz Telemetry Rate**  
   Achieved via `usleep(50000)` in C.  
   (Similar to many UAV telemetry systems.)

3. **Float Precision**  
   Output values are formatted to ~2-3 decimal precision, suitable for logging.

4. **Pipe Mode Used Instead of Serial Port**  
   MSYS2 environment allows easy piping without needing USB-UART adapters.  
   This keeps the entire pipeline reproducible on any machine.

5. **No Visualization**  
   As per Level-1 instructions, only terminal formatting and CSV logging were implemented.

---

## 🤖 AI Tools Used

This project was developed with the assistance of:
- **ChatGPT** for:
  - Code structuring guidance
  - Comment explanations
  - Professional formatting and documentation help

All code was **written and understood by me**, with AI used only for learning support and refinement.

---

## 📝 Notes for Reviewers (AIRMAN Team)

- Telemetry format strictly matches the assignment specification.  
- XOR checksum validated against transmitter logic.  
- Modular design used to separate sensor models and protocol logic.  
- The receiver design mimics real-world ground-station parsing.  
- The overall approach focuses on clarity, correctness, and maintainable firmware style.

---

## 🚀 Final Status

**Level 1 implementation: COMPLETE**  
Telemetry successfully runs end-to-end with proper checksum validation and CSV logging.


