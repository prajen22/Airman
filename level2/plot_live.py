"""
uart_rx_level2_logger.py

AIRMAN – Level 2 Telemetry Receiver & Logger
--------------------------------------------

This script acts as the Ground Station telemetry ingestion layer
for the Level-2 AHRS system.

Core Responsibilities:
- Receive Level-2 telemetry frames via STDIN (pipe mode)
- Validate frame integrity using CRC16-CCITT
- Parse AHRS and environmental data
- Log validated telemetry into a CSV flight log

Design Philosophy:
- Keep ingestion simple, deterministic, and reliable
- Separate logging from visualization (clean architecture)
- Mimic real-world ground station data recorders used
  during flight testing and system integration
"""

import sys
import csv

# ============================================================
# CRC16-CCITT IMPLEMENTATION
# ============================================================
#
# Polynomial : 0x1021
# Init value : 0xFFFF
#
# CRC16 is widely used in aerospace, automotive, and embedded
# communication systems because it provides much stronger
# error detection than simple XOR checksums.
#

def calculate_crc16(payload: str) -> int:
    """
    Compute CRC16-CCITT checksum for a given payload string.

    The checksum is calculated over the exact payload content
    (everything between '$' and '*').

    Args:
        payload (str): Telemetry payload string

    Returns:
        int: 16-bit CRC value
    """
    crc = 0xFFFF

    for ch in payload:
        crc ^= ord(ch) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF

    return crc

# ============================================================
# TELEMETRY FRAME PARSER
# ============================================================

def parse_line(line: str):
    """
    Parse and validate a single Level-2 telemetry frame.

    Expected frame format:
    $L2,<timestamp_ms>,<roll>,<pitch>,<heading>,<alt>,<temp>*<CRC16>

    Validation steps:
    1. Check frame start ('$') and checksum delimiter ('*')
    2. Extract payload and received CRC
    3. Recalculate CRC and compare
    4. Validate field count and frame type

    Args:
        line (str): Raw telemetry line

    Returns:
        tuple or None:
            (timestamp_ms, roll, pitch, heading, altitude, temperature)
            if frame is valid, otherwise None
    """

    # Basic structural validation
    if not line.startswith("$") or "*" not in line:
        return None

    # Extract payload (without '$' and checksum)
    payload = line[1:line.index("*")]

    # Parse received CRC
    try:
        recv_crc = int(line.split("*")[1], 16)
    except ValueError:
        return None

    # Verify CRC integrity
    if calculate_crc16(payload) != recv_crc:
        return None

    # Split CSV fields
    parts = payload.split(",")

    # Validate Level-2 frame structure
    if len(parts) != 7 or parts[0] != "L2":
        return None

    _, ts, roll, pitch, yaw, alt, temp = parts

    return ts, roll, pitch, yaw, alt, temp

# ============================================================
# MAIN LOGGING LOOP
# ============================================================
#
# This loop continuously reads telemetry frames from STDIN,
# validates them, and logs only correct frames to CSV.
#
# Using sys.stdin.buffer ensures compatibility with Windows
# piping and avoids encoding-related issues.
#

print("📡 Level-2 telemetry logger started")
print("📁 Logging to level2_telemetry.csv")

with open("level2_telemetry.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file)

    # CSV header mirrors telemetry payload fields
    writer.writerow(
        ["timestamp_ms", "roll", "pitch", "heading", "altitude", "temperature"]
    )

    # Read incoming telemetry frames (pipe mode)
    for raw in sys.stdin.buffer:
        line = raw.decode(errors="ignore").strip()

        parsed = parse_line(line)
        if parsed:
            writer.writerow(parsed)
            csv_file.flush()
