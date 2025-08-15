// ===== MAIN OPERATIONAL SKETCH - V7 (UDP enabled) =====

#include <SCServo.h>
#include <WiFi.h>
#include <WiFiUdp.h>

SMS_STS st;

// UART pins for servo communication
#define S_RXD 18
#define S_TXD 19

// --- Servo Configuration ---
const int HOME_POSITION = 2048; 

// --- Timing variables ---
unsigned long lastMoveTime_Pan = 0;
unsigned long nextMoveDelay_Pan = 1000;
unsigned long lastMoveTime_Tilts = 0;
unsigned long nextMoveDelay_Tilts = 2000;

// --- UDP / AP Configuration ---
const char* ssid = "Eric_AP";
const char* password = "12345678"; // optional
WiFiUDP Udp;
const unsigned int localUdpPort = 4210;
char incomingPacket[256]; // safe buffer
int audioOffset = 0; // micromovement for Servo 3
const int MAX_AUDIO_OFFSET = 20; // named constant for clarity

void setup() {
    Serial.begin(115200);
    Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD);
    st.pSerial = &Serial1;

    randomSeed(analogRead(A0));

    Serial.println("--- Main Sketch V7 Starting Up ---");
    Serial.println("Homing all servos to their calibrated center positions...");

    // Home all servos simultaneously
    st.WritePosEx(1, HOME_POSITION, 800, 50); // Pan
    st.WritePosEx(2, HOME_POSITION, 800, 50); // Tilt torso
    st.WritePosEx(3, HOME_POSITION, 800, 50); // Tilt head
    delay(4000); // wait for homing

    // --- Tiny visualisation of Servo 2 forward movement ---
    long testForwardPos = HOME_POSITION + 10; 
    st.WritePosEx(2, testForwardPos, 500, 10); // gentle movement
    delay(500);
    st.WritePosEx(2, HOME_POSITION, 500, 10); 
    delay(300);

    // --- Start ESP32 AP ---
    WiFi.softAP(ssid, password);
    Serial.print("AP started. IP address: ");
    Serial.println(WiFi.softAPIP());

    // Start UDP listener
    Udp.begin(localUdpPort);
    Serial.printf("UDP listener started on port %u\n", localUdpPort);
}

void loop() {
    unsigned long currentMillis = millis();

    // --- Servo 1 (Pan) Logic ---
    if ((currentMillis - lastMoveTime_Pan) >= nextMoveDelay_Pan) {
        long newPos = random(HOME_POSITION - 400, HOME_POSITION + 400); // ±400 steps
        long newSpeed = random(1000, 2500);
        nextMoveDelay_Pan = random(1500, 4000);

        Serial.printf("Servo 1 (Pan) moving to: %ld\n", newPos);
        st.WritePosEx(1, newPos, newSpeed, 80);

        lastMoveTime_Pan = currentMillis;
    }

    // --- Servos 2 & 3 (Tilts: forward/backward) Logic ---
    if ((currentMillis - lastMoveTime_Tilts) >= nextMoveDelay_Tilts) {
        long tiltOffset = random(-171, 172); // ±171 steps
        long newSpeed = random(800, 1400);
        nextMoveDelay_Tilts = random(2000, 6000);

        long newPos2 = HOME_POSITION + tiltOffset; // Servo 2 (torso tilt)
        long newPos3 = HOME_POSITION + tiltOffset + audioOffset; // Servo 3 (head tilt with audio)

        // Constrain to safe ranges
        // Pan ±400, Tilts ±171 (forward limited by cables)
        newPos2 = constrain(newPos2, HOME_POSITION - 171, HOME_POSITION + 171);
        newPos3 = constrain(newPos3, HOME_POSITION - 171, HOME_POSITION + 171);

        Serial.printf("Servos 2&3 (Tilts) moving by offset: %ld\n", tiltOffset);

        st.WritePosEx(2, newPos2, newSpeed, 80);
        st.WritePosEx(3, newPos3, newSpeed, 80);

        lastMoveTime_Tilts = currentMillis;
    }

    // --- UDP Packet Handling (non-blocking) ---
    int packetSize = Udp.parsePacket();
    if (packetSize) {
        int len = Udp.read(incomingPacket, 255); // leave room for null terminator
        if (len > 0) incomingPacket[len] = '\0';

        // Safer number parsing
        char* endptr;
        long amp = strtol(incomingPacket, &endptr, 10);
        if (*endptr == '\0') { // valid number
            amp = constrain(amp, 0, 100); 
            audioOffset = map(amp, 0, 100, -MAX_AUDIO_OFFSET, MAX_AUDIO_OFFSET);
        }
    } else {
        // Gradually decay audioOffset back to 0
        if (audioOffset > 0) audioOffset--;
        else if (audioOffset < 0) audioOffset++;
    }
}