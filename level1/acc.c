#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

// Generate random noise between -amp to +amp
float noise(float amp) {
    return ((float)rand() / RAND_MAX) * (2 * amp) - amp;
}

// Simulate high-quality accelerometer (Very impressive pattern)
float simulate_accel_x(int t) {
    float base = 0.8 * sin(t * 0.02);       // main motion
    float secondary = 0.3 * sin(t * 0.005); // slow motion
    float vibration = 0.05 * sin(t * 0.5);  // vibration
    return base + secondary + vibration + noise(0.1);
}

float simulate_accel_y(int t) {
    float base = 0.8 * cos(t * 0.018 + 1.0); // phase shifted motion
    float secondary = 0.2 * sin(t * 0.008);
    float vibration = 0.05 * sin(t * 0.45);
    return base + secondary + vibration + noise(0.1);
}

float simulate_accel_z(int t) {
    float gravity = 9.81;                   // Earth gravity
    float vibration = 0.03 * sin(t * 0.4);  // vibration on Z
    return gravity + vibration + noise(0.05);
}

int main() {
    srand(time(NULL));
    int t = 0;

    while (1) {
        float ax = simulate_accel_x(t);
        float ay = simulate_accel_y(t);
        float az = simulate_accel_z(t);

        printf("AX: %.3f  AY: %.3f  AZ: %.3f\n", ax, ay, az);

        usleep(50000); // 50 ms (20 Hz)
        t++;
    }

    return 0;
}
