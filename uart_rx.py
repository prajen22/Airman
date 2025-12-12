import sys
import csv

# =============================================================================
# XOR CHECKSUM
# =============================================================================
# Many lightweight telemetry protocols (especially in UAVs and robotics)
# use XOR-based checksums because they are:
#   - Fast to compute on low-power microcontrollers
#   - Able to detect single-bit errors in noisy UART links
#   - Simple enough to implement in both C and Python
#
# The transmitter (telemetry_tx.c) computes the XOR over the payload bytes
# between '$' and '*'. The receiver repeats the same calculation here and
# compares the result to validate frame integrity.
# =============================================================================
def calculate_checksum(payload: str) -> int:
    chk = 0
    for ch in payload:
        chk ^= ord(ch)
    return chk


# =============================================================================
# PROCESS A SINGLE TELEMETRY FRAME
# =============================================================================
# Each incoming line represents one complete telemetry frame.
# This function:
#   - Cleans the raw string
#   - Extracts payload and checksum
#   - Validates checksum
#   - Splits telemetry fields
#   - Logs them into CSV
#   - Prints a readable summary for the operator
#
# The design mirrors how ground-control stations validate flight telemetry.
# =============================================================================
def process_frame(line, writer):
    line = line.strip()

    # Basic framing validation
    if not line.startswith("$"):
        # '$' indicates start-of-frame in many aviation protocols
        print("Invalid frame (missing $):", line)
        return

    if "*" not in line:
        # '*' separates payload from checksum
        print("Invalid frame (missing *):", line)
        return

    # Extract payload and received checksum
    payload = line[1:line.index("*")]
    recv_chk_hex = line.split("*")[1]

    # Convert received HEX checksum into integer
    try:
        recv_chk = int(recv_chk_hex, 16)
    except:
        print("Invalid checksum format:", recv_chk_hex)
        return

    # Recalculate checksum on received payload
    calc_chk = calculate_checksum(payload)

    if recv_chk != calc_chk:
        # Mismatched checksums indicate UART noise or frame corruption
        print(f"Checksum error: recv={recv_chk_hex} calc={calc_chk:02X}")
        return

    # Split by CSV fields
    parts = payload.split(",")
    if len(parts) != 10:
        # A valid Level-1 frame must have exactly 10 fields
        print("Invalid field count:", parts)
        return

    label, ts, ax, ay, az, gx, gy, gz, alt, temp = parts

    # Write clean numeric data to CSV for offline analysis
    writer.writerow([ts, ax, ay, az, gx, gy, gz, alt, temp])

    # Human-friendly output for consoles/ground stations
    print(f"[{ts} ms] ACC=({ax},{ay},{az})  "
          f"GYRO=({gx},{gy},{gz})  ALT={alt}  TEMP={temp}")


# =============================================================================
# MAIN LOOP — READ FROM STDIN (PIPE MODE)
# =============================================================================
# Instead of requiring real UART hardware, the receiver accepts telemetry
# frames from standard input (stdin). This allows:
#   - Easy testing on any PC
#   - Simple integration with MSYS2 or Linux pipes
#   - Identical behavior to reading from a serial port
#
# Usage:
#   ./telemetry_tx | python uart_rx.py
#
# This is a clean, reproducible method recommended for offline telemetry testing.
# =============================================================================
def main():
    print("=== AIRMAN Telemetry Receiver ===")
    print("Reading telemetry from STDIN (pipe mode)...")
    print("Press CTRL+C to stop.\n")

    # Prepare CSV file for logging decoded sensor values
    csv_file = open("output.csv", "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz", "alt", "temp"])

    # Continuously read incoming telemetry frames
    for line in sys.stdin:
        process_frame(line, writer)

    csv_file.close()


if __name__ == "__main__":
    main()
