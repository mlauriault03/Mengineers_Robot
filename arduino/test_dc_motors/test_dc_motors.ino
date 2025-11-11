// DRV8838 + Arduino MKR Zero
// Pot controls speed & direction (center = stop)
// Pins: PHASE = direction, IN = PWM speed, nSLEEP = enable

const int PIN_PHASE  = 2;      // Direction (PHASE)
const int PIN_IN     = 5;      // PWM speed (IN)  <-- must be PWM-capable
const int PIN_SLEEP  = 4;      // nSLEEP (HIGH = enabled)
const int PIN_POT    = A1;     // Pot center wiper

// Tuning
const int DEAD_BAND  = 25;     // +/- around center to treat as "stop"
const int FILTER     = 4;      // Simple smoothing of the pot reading
int filt = 512;

void setup() {
  pinMode(PIN_PHASE, OUTPUT);
  pinMode(PIN_IN,    OUTPUT);
  pinMode(PIN_SLEEP, OUTPUT);

  digitalWrite(PIN_SLEEP, HIGH);  // wake the driver
  analogWrite(PIN_IN, 0);         // start stopped

  Serial.begin(115200);
  while (!Serial) {}
  Serial.println("DRV8838 DC Motor: Pot controls speed & direction (center = stop)");
}

void loop() {
  // Read pot (0..1023) and lightly smooth it
  int raw = analogRead(PIN_POT);
  filt = (filt * FILTER + raw) / (FILTER + 1);

  // Map around center to signed speed: -255..+255 with a deadband
  int signedSpeed = 0;
  if (filt > 512 + DEAD_BAND) {
    signedSpeed = map(filt, 512 + DEAD_BAND, 1023, 0, 255);     // forward
  } else if (filt < 512 - DEAD_BAND) {
    signedSpeed = -map(filt, 512 - DEAD_BAND, 0, 0, 255);       // reverse
  } else {
    signedSpeed = 0;  // stop (deadband)
  }

  driveMotor(signedSpeed);

  // Optional debug
  static uint32_t t0 = 0;
  if (millis() - t0 > 200) {
    t0 = millis();
    Serial.print("POT: "); Serial.print(filt);
    Serial.print("  Speed: "); Serial.println(signedSpeed);
  }
}

void driveMotor(int v) {
  if (v == 0) {
    // Brake (fast stop): IN = 0
    analogWrite(PIN_IN, 0);
    // PHASE can be left as-is
    return;
  }

  if (v > 0) {
    digitalWrite(PIN_PHASE, HIGH);     // forward
    analogWrite(PIN_IN, v);            // 1..255
  } else {
    digitalWrite(PIN_PHASE, LOW);      // reverse
    analogWrite(PIN_IN, -v);           // 1..255
  }
}
