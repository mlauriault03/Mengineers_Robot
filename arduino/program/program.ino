// Main Arduino Program
// 11/11/25


// ---------- PINS ----------
// motor 1
const int PIN_PHASE1  = 4;      // Direction (PHASE)
const int PIN_IN1     = 6;      // PWM speed (IN)  <-- must be PWM-capable
// motor 2
const int PIN_PHASE2  = 3;      // Direction (PHASE)
const int PIN_IN2     = 7;      // PWM speed (IN)  <-- must be PWM-capable
// motor 3
const int PIN_PHASE3  = 2;      // Direction (PHASE)
const int PIN_IN3     = 5;      // PWM speed (IN)  <-- must be PWM-capable


// ---------- COMMANDS ----------
const String MOTOR1 = "MOTOR1"; // Keypad
const String MOTOR2 = "MOTOR2"; // Extender
const String MOTOR3 = "MOTOR3"; // Crank
// (Add more commands as needed...)


// ---------- SUB-ROUTINES ----------
void drive_motor(int motor, int speed) {
  /* Turn specified motor at given speed
  PARAMETERS:
    motor: number of the motor to control (ex. 1 for motor1)
    speed: speed at which to turn the motor:
      -255 = full reverse
      0 = stop
      255 = full forward
  */
  int pin_phase;
  int pin_in;
  // Determine motor pins
  switch (motor) {
    case 1:
      pin_phase = PIN_PHASE1;
      pin_in = PIN_IN1;
      break;
    case 2:
      pin_phase = PIN_PHASE2;
      pin_in = PIN_IN2;
      break;
    case 3:
      pin_phase = PIN_PHASE3;
      pin_in = PIN_IN3;
      break;
    default:
      Serial.print("Unknown motor");
      Serial.println(motor);
      break;
  }
  // if stop
  if (speed == 0) {
    // Brake (fast stop): IN = 0
    analogWrite(pin_in, 0);
    // PHASE can be left as-is
    return;
  }
  // if forward
  if (speed > 0) {
    digitalWrite(pin_phase, HIGH);     // forward
    analogWrite(pin_in, speed);        // 1 to 255
  // if reverse
  } else {
    digitalWrite(pin_phase, LOW);      // reverse
    analogWrite(pin_in, -speed);       // 1 to 255
  }
}


// ---------- INITIAL SETUP ----------
void setup() {
  // set pin input/output modes
  pinMode(PIN_PHASE1, OUTPUT);
  pinMode(PIN_IN1,    OUTPUT);
  pinMode(PIN_PHASE2, OUTPUT);
  pinMode(PIN_IN2,    OUTPUT);
  pinMode(PIN_PHASE3, OUTPUT);
  pinMode(PIN_IN3,    OUTPUT);
  // start all drivers
  analogWrite(PIN_IN1, 0);
  analogWrite(PIN_IN2, 0);
  analogWrite(PIN_IN3, 0);
  // start serial monitor
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Arduino ready");
}


// ---------- FOREVER LOOP ----------
void loop() {
  // Wait for serial port
  if (Serial.available()) {
    // Parse command
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    // Handle command
    if (cmd == MOTOR1) {
      Serial.println("Turning motor 1 (keypad)...");
      drive_motor(1, -255);
      delay(5000);
      drive_motor(1, 0);
      Serial.println("Turned motor 1");
    } else if (cmd == MOTOR2) {
      Serial.println("Turning motor 2 (extender)...");
      drive_motor(2, 255);
      delay(4000);
      drive_motor(2, -255);
      delay(4000);
      drive_motor(2, 0);
      Serial.println("Turned motor 2");
    } else if (cmd == MOTOR3) {
      Serial.println("Turning motor 3 (crank)...");
      drive_motor(3, -255);
      delay(5000);
      drive_motor(3, 0);
      Serial.println("Turned motor 3");
    } else if (cmd == "reset") {
      drive_motor(2, -255);
      delay(250);
      drive_motor(2, 0);
    } else {
      Serial.print("Unknown command: ");
        Serial.println(cmd);
    }
  }
}