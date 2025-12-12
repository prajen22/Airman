        #include <stdio.h>
        #include <stdlib.h>
        #include <math.h>
        #include <time.h>
        #include <unistd.h>

        /*
        * Generate pseudo-random noise between -amp and +amp.
        * Real-world sensors (IMUs, altimeters, thermistors) always contain electrical noise,
        * quantization errors, and mechanical vibration. Adding noise makes simulated data
        * behave like true physical sensors.
        */
        float noise(float amp) {
            return ((float)rand() / RAND_MAX) * (2 * amp) - amp;
        }

        /* ============================================================
        *               ACCELEROMETER SIMULATION
        * ============================================================
        *
        * Accelerometer measures:
        *   - Linear motion (forward/back, left/right, up/down)
        *   - Constant gravity on Z axis
        *   - High-frequency vibration from motors / environment
        *   - Sensor noise + drift
        *
        * We combine:
        *   1. Primary oscillation       → body movement
        *   2. Slow drift                → long-term motion trend
        *   3. Vibration                 → motor/airframe vibration
        *   4. Random noise              → sensor imperfections
        *   5. Constant gravity on Z
        */

        float simulate_accel_x(int t) {
            float primary   = 0.8 * sin(t * 0.02);
            float secondary = 0.3 * sin(t * 0.005);
            float vibration = 0.05 * sin(t * 0.50);
            return primary + secondary + vibration + noise(0.1);
        }

        float simulate_accel_y(int t) {
            float primary   = 0.8 * cos(t * 0.018 + 1.0); // phase-shifted for realism
            float secondary = 0.2 * sin(t * 0.008);
            float vibration = 0.05 * sin(t * 0.45);
            return primary + secondary + vibration + noise(0.1);
        }

        float simulate_accel_z(int t) {
            float gravity   = 9.81;                      // constant Earth gravity
            float vibration = 0.03 * sin(t * 0.40);      // subtle vertical vibration
            return gravity + vibration + noise(0.05);
        }

        /* ============================================================
        *                   GYROSCOPE SIMULATION
        * ============================================================
        *
        * Gyroscope measures angular velocity (degrees/sec or rad/sec):
        *    - Roll  (gx)
        *    - Pitch (gy)
        *    - Yaw   (gz)
        *
        * Characteristics included:
        *    1. Smooth rotation       → sin/cos waves
        *    2. Low-frequency drift   → natural gyro bias drift
        *    3. High-frequency noise  → jitter
        *    4. Occasional spikes     → sudden small jerks
        */

        float simulate_gyro_x(int t) {
            float rotation  = 3.0 * sin(t * 0.008);  // slow roll oscillation
            float drift     = 0.2 * sin(t * 0.0005);
            float spike     = (t % 500 == 0) ? noise(1.0) : 0; // occasional jerk
            return rotation + drift + spike + noise(0.2);
        }

        float simulate_gyro_y(int t) {
            float rotation  = 3.0 * cos(t * 0.007);  // slow pitch oscillation
            float drift     = 0.2 * sin(t * 0.0007);
            float spike     = (t % 700 == 0) ? noise(0.8) : 0;
            return rotation + drift + spike + noise(0.2);
        }

        float simulate_gyro_z(int t) {
            float rotation  = 20.0 * sin(t * 0.01);  // stronger yaw (turning)
            float drift     = 0.5 * sin(t * 0.0004);
            return rotation + drift + noise(0.3);
        }

        /* ============================================================
        *                    ALTITUDE SIMULATION
        * ============================================================
        *
        * Altitude typically:
        *   - Changes slowly
        *   - Has small sinusoidal fluctuations due to air pressure
        *   - Has environmental noise
        *
        * We simulate:
        *   1. Slow linear climb        → drone/robot gaining altitude
        *   2. Pressure wobble          → small sine fluctuation
        *   3. Noise                    → realistic sensor readings
        */

        float simulate_altitude(int t) {
            float climb     = 100 + (t * 0.02);       // ascending slowly
            float wobble    = 0.3 * sin(t * 0.04);    // pressure variation
            return climb + wobble + noise(0.2);
        }

        /* ============================================================
        *                   TEMPERATURE SIMULATION
        * ============================================================
        *
        * Temperature changes VERY slowly in real systems.
        * We simulate:
        *   1. Base temperature
        *   2. Slow heating drift
        *   3. Tiny random fluctuations
        *   4. Low-pass filtering for smoothness
        */

        float simulate_temperature(int t, float prev_temp) {
            float base       = 30.0;
            float heating    = 0.0008 * t;           // slow rise
            float fluct      = noise(0.2);

            float raw = base + heating + fluct;

            // Low-pass filter → smoother, more realistic temperature signal
            return prev_temp * 0.95 + raw * 0.05;
        }

/* ============================================================
 *                  XOR CHECKSUM CALCULATION
 * ============================================================
 *
 * Many aviation and UAV telemetry protocols use XOR checksums due to their
 * simplicity and computational efficiency. The checksum is computed over
 * all bytes between '$' and '*', enabling the ground station or receiver
 * to validate frame integrity over noisy UART links.
 */
unsigned char calculate_checksum(const char *buf) {
    unsigned char chk = 0;
    while (*buf) {
        chk ^= (unsigned char)*buf;  // XOR each payload byte
        buf++;
    }
    return chk;
}

/* ============================================================
 *                   MAIN LOOP (WITH CHECKSUM)
 * ============================================================ */
int main() {
    srand(time(NULL));

    int t = 0;
    float temp = 30.0;

    while (1) {

        float ax = simulate_accel_x(t);
        float ay = simulate_accel_y(t);
        float az = simulate_accel_z(t);

        float gx = simulate_gyro_x(t);
        float gy = simulate_gyro_y(t);
        float gz = simulate_gyro_z(t);

        float alt = simulate_altitude(t);

        temp = simulate_temperature(t, temp);

        /* -------------------------------------------------------
         * Build telemetry payload (without '$' and '*')
         * ------------------------------------------------------- */
        char payload[256];
        sprintf(payload,
            "L1,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%.2f",
            t * 50,  // timestamp in ms
            ax, ay, az, gx, gy, gz, alt, temp
        );

        /* Compute XOR checksum */
        
        unsigned char chk = calculate_checksum(payload);

        /* Build final frame */
        char frame[300];
        sprintf(frame, "$%s*%02X", payload, chk);

        /* Print final telemetry frame */
        printf("%s\n", frame);

        usleep(50000); // 50 ms → 20 Hz
        t++;
    }

    return 0;
}

       
        