/*
 * telemetry_tx_level2_realworld_crc16.c
 *
 * AIRMAN – Level 2 AHRS Telemetry Transmitter
 * ------------------------------------------
 *
 * This file implements a real-world style Level-2 telemetry transmitter,
 * similar to what would run on an embedded flight controller or robotic
 * compute unit during system integration.
 *
 * Architecture Overview:
 *   1) Sensor Acquisition Layer
 *        - Simulated IMU (accelerometer, gyroscope, magnetometer)
 *        - Designed to mimic realistic sensor behavior with noise
 *
 *   2) AHRS Estimation Layer
 *        - Madgwick filter (quaternion-based orientation estimation)
 *        - Converts raw IMU data into roll, pitch, and heading
 *
 *   3) Telemetry Encoding Layer
 *        - UART-style ASCII telemetry frames
 *        - CRC16-CCITT checksum for robust error detection
 *
 * Telemetry Frame Format:
 *   $L2,<timestamp_ms>,<roll>,<pitch>,<heading>,<alt>,<temp>*<CRC16>
 *
 * Timing:
 *   - Fixed update rate: 20 Hz (50 ms)
 *   - Deterministic loop timing (no dynamic delays)
 *
 * Checksum:
 *   - CRC16-CCITT
 *   - Polynomial: 0x1021
 *   - Initial value: 0xFFFF
 *
 * This design mirrors how embedded telemetry is structured in
 * UAVs, robotics platforms, and avionics test systems.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <unistd.h>
#include <sys/time.h>
#include <time.h>

/* ============================================================
 * CONFIGURATION
 * ============================================================
 *
 * LOOP_HZ defines the telemetry update rate.
 * LOOP_DT_SEC is used by the AHRS algorithm as the integration
 * timestep, ensuring consistent filter behavior.
 */

#define LOOP_HZ        20
#define LOOP_DT_SEC    (1.0f / LOOP_HZ)

/* ============================================================
 * UTILITY FUNCTIONS
 * ============================================================
 *
 * Simple helpers for unit conversion and checksum computation.
 * These are kept small and explicit for clarity and portability.
 */

static float deg2rad(float d) { return d * (M_PI / 180.0f); }
static float rad2deg(float r) { return r * (180.0f / M_PI); }

/*
 * CRC16-CCITT checksum implementation
 *
 * Why CRC16 instead of XOR:
 *   - XOR is fast but weak against many error patterns
 *   - CRC16 detects burst errors and bit inversions reliably
 *   - Commonly used in aviation, telemetry radios, and serial protocols
 *
 * Parameters:
 *   Polynomial : 0x1021
 *   Init value : 0xFFFF
 */
static unsigned short crc16_ccitt(const char *data)
{
    unsigned short crc = 0xFFFF;

    while (*data) {
        crc ^= ((unsigned short)(*data++) << 8);
        for (int i = 0; i < 8; i++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}

/* ============================================================
 * TIME BASE (REAL SYSTEM STYLE)
 * ============================================================
 *
 * Embedded systems typically maintain a monotonic millisecond
 * counter since boot. This function replicates that behavior
 * using gettimeofday for a PC-based environment.
 */

static long long millis_since(struct timeval *start)
{
    struct timeval now;
    gettimeofday(&now, NULL);

    return (now.tv_sec - start->tv_sec) * 1000LL +
           (now.tv_usec - start->tv_usec) / 1000LL;
}

/* ============================================================
 * SENSOR LAYER — IMU SIMULATION
 * ============================================================
 *
 * This layer simulates an IMU device.
 *
 * Design goals:
 *   - Deterministic motion patterns
 *   - Realistic sensor noise
 *   - Stable gravity vector
 *
 * This allows the AHRS algorithm to be tested exactly as it
 * would be with real hardware, without requiring physical sensors.
 */

typedef struct {
    float ax, ay, az;   // Accelerometer (m/s²)
    float gx, gy, gz;   // Gyroscope (deg/s)
    float mx, my, mz;   // Magnetometer (normalized)
} imu_sample_t;

/* Generate small random noise to simulate sensor imperfections */
static float noise(float amp)
{
    return ((float)rand() / RAND_MAX) * 2.0f * amp - amp;
}

static void imu_read(imu_sample_t *imu, int t)
{
    /* Accelerometer:
     *   - Sinusoidal motion in X/Y
     *   - Constant gravity on Z
     *   - Added noise to simulate vibration and ADC noise
     */
    imu->ax = 0.6f * sinf(t * 0.02f) + noise(0.05f);
    imu->ay = 0.6f * cosf(t * 0.02f) + noise(0.05f);
    imu->az = 9.81f + noise(0.08f);

    /* Gyroscope (deg/s):
     *   - Low, steady angular rates
     *   - Small noise to simulate bias and jitter
     */
    imu->gx = 2.0f  + noise(0.2f);
    imu->gy = 1.5f  + noise(0.2f);
    imu->gz = 12.0f + noise(0.3f);

    /* Magnetometer:
     *   - Normalized Earth magnetic field
     *   - Noise simulates environmental interference
     */
    imu->mx = 0.3f + noise(0.02f);
    imu->my = 0.0f + noise(0.02f);
    imu->mz = 0.5f + noise(0.02f);
}

/* ============================================================
 * AHRS LAYER — MADGWICK FILTER
 * ============================================================
 *
 * Quaternion-based orientation estimation.
 *
 * Why Madgwick:
 *   - Computationally efficient
 *   - Stable for real-time systems
 *   - Widely used in UAVs and robotics
 *
 * This implementation focuses on clarity and correctness rather
 * than micro-optimizations.
 */

static float q0 = 1.0f, q1 = 0.0f, q2 = 0.0f, q3 = 0.0f;

static float inv_sqrt(float x)
{
    return 1.0f / sqrtf(x);
}

static void madgwick_update(const imu_sample_t *imu, float dt)
{
    float ax = imu->ax, ay = imu->ay, az = imu->az;
    float gx = deg2rad(imu->gx);
    float gy = deg2rad(imu->gy);
    float gz = deg2rad(imu->gz);
    float mx = imu->mx, my = imu->my, mz = imu->mz;

    /* Normalize accelerometer */
    float norm = sqrtf(ax*ax + ay*ay + az*az);
    if (norm == 0.0f) return;
    ax /= norm; ay /= norm; az /= norm;

    /* Normalize magnetometer */
    norm = sqrtf(mx*mx + my*my + mz*mz);
    if (norm == 0.0f) return;
    mx /= norm; my /= norm; mz /= norm;

    /* Quaternion rate of change from gyroscope */
    float qDot0 = 0.5f * (-q1*gx - q2*gy - q3*gz);
    float qDot1 = 0.5f * ( q0*gx + q2*gz - q3*gy);
    float qDot2 = 0.5f * ( q0*gy - q1*gz + q3*gx);
    float qDot3 = 0.5f * ( q0*gz + q1*gy - q2*gx);

    /* Integrate quaternion */
    q0 += qDot0 * dt;
    q1 += qDot1 * dt;
    q2 += qDot2 * dt;
    q3 += qDot3 * dt;

    /* Normalize quaternion */
    norm = inv_sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3);
    q0 *= norm; q1 *= norm; q2 *= norm; q3 *= norm;
}

/* Convert quaternion to Euler angles (degrees) */
static void ahrs_get_euler(float *roll, float *pitch, float *yaw)
{
    *roll  = rad2deg(atan2f(2*(q0*q1 + q2*q3),
                            1 - 2*(q1*q1 + q2*q2)));
    *pitch = rad2deg(asinf(2*(q0*q2 - q3*q1)));
    *yaw   = rad2deg(atan2f(2*(q0*q3 + q1*q2),
                            1 - 2*(q2*q2 + q3*q3)));
}

/* ============================================================
 * MAIN CONTROL LOOP
 * ============================================================
 *
 * Fixed-rate control loop:
 *   - Read sensors
 *   - Update AHRS
 *   - Encode telemetry frame
 *   - Transmit over stdout (UART-style)
 */

int main(void)
{
    srand(time(NULL));

    struct timeval boot_time;
    gettimeofday(&boot_time, NULL);

    int t = 0;

    while (1) {

        imu_sample_t imu;
        imu_read(&imu, t);

        madgwick_update(&imu, LOOP_DT_SEC);

        float roll, pitch, yaw;
        ahrs_get_euler(&roll, &pitch, &yaw);

        /* Simulated environment data */
        float altitude    = 100.0f + 0.05f * t;
        float temperature = 30.0f;

        long long ts = millis_since(&boot_time);

        /* Build telemetry payload (checksum excludes $ and *) */
        char payload[200];
        snprintf(payload, sizeof(payload),
                 "L2,%lld,%.2f,%.2f,%.2f,%.2f,%.2f",
                 ts, roll, pitch, yaw, altitude, temperature);

        /* Compute CRC16 checksum */
        unsigned short crc = crc16_ccitt(payload);

        /* Transmit final frame */
        printf("$%s*%04X\n", payload, crc);
        fflush(stdout);

        usleep(50000);  /* 20 Hz loop */
        t++;
    }

    return 0;
}
