// Servo Test with Potentiometer Control
// 11/7/25

#include <Servo.h>

Servo myServo;

const int servoPin = 6;     // PWM pin for servo
const int potPin = A1;      // Analog pin for potentiometer
int speed = 90;             // Servo speed (90=stop, 0=fastest)

void setup() {
    myServo.attach(servoPin);
    Serial.begin(9600);
    while (!Serial);
    Serial.println("Servo speed controlled by potentiometer.");
}

void loop() {
    int potValue = analogRead(potPin); // Read the potentiometer (0 to 1023)
    speed = map(potValue, 0, 1020, 0, 90); // Map the potentiometer value to a speed
    myServo.write(speed); // Sets the speed for continous servos, but sets the position for standard positional servos
    delay(10); // brief delay for stability

    // Optional: Print current status
    Serial.print("Potentiometer: "); Serial.print(potValue);
    Serial.print(" Speed: "); Serial.println(speed);
}