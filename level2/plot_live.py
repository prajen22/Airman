import sys
import csv

"""
uart_rx_level2_logger.py

Level-2 telemetry receiver & logger (CRC16-CCITT).

Responsibilities:
- Read telemetry frames from STDIN (pipe mode)
- Validate CRC16-CCITT checksum
- Parse Level-2 AHRS telemetry
- Log valid data to CSV

This design mirrors real ground-station logging tools where
telemetry ingestion is kept simple, deterministic, and reliable.
"""

# ============================================================
# CRC16-CCITT (poly 0x1021, init 0xFFFF)
# ============================================================

def calculate_crc16(payload: str) -> int:
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
# Telemetry frame parser
# ============================================================

def parse_line(line: str):
    """
    Expected frame format:
    $L2,<timestamp_ms>,<roll>,<pitch>,<heading>,<alt>,<temp>*<CRC16>
    """

    if not line.startswith("$") or "*" not in line:
        return None

    payload = line[1:line.index("*")]

    try:
        recv_crc = int(line.split("*")[1], 16)
    except ValueError:
        return None

    # Validate CRC
    if calculate_crc16(payload) != recv_crc:
        return None

    parts = payload.split(",")
    if len(parts) != 7 or parts[0] != "L2":
        return None

    _, ts, roll, pitch, yaw, alt, temp = parts

    return ts, roll, pitch, yaw, alt, temp

# ============================================================
# Main logging loop
# ============================================================

print("📡 Level-2 telemetry logger started")
print("📁 Logging to level2_telemetry.csv")

with open("level2_telemetry.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(
        ["timestamp_ms", "roll", "pitch", "heading", "altitude", "temperature"]
    )

    # Read raw bytes from stdin (Windows-safe)
    for raw in sys.stdin.buffer:
        line = raw.decode(errors="ignore").strip()
        parsed = parse_line(line)

        if parsed:
            writer.writerow(parsed)
            csv_file.flush()
