

#include <Servo.h>
#include <stdio.h>

const uint8_t MOTOR_EN_PIN = 5;
const uint8_t MOTOR_IN1_PIN = 6;
const uint8_t MOTOR_IN2_PIN = 7;
const uint8_t SONAR_TRIG_PIN = 8;
const uint8_t SONAR_ECHO_PIN = 9;
const uint8_t STEERING_SERVO_PIN = 10;

const unsigned long SERIAL_BAUD = 115200UL;
const unsigned long SENSOR_INTERVAL_MS = 100UL;
const unsigned long TELEMETRY_INTERVAL_MS = 100UL;
const unsigned long COMMAND_TIMEOUT_MS = 600UL;
const unsigned long SENSOR_TIMEOUT_MS = 350UL;

const float MIN_DISTANCE_CM = 25.0f;
const float MAX_DISTANCE_CM = 400.0f;

Servo steeringServo;

char inputLine[48];
uint8_t inputIndex = 0;

int requestedSteeringDeg = 90;
int requestedThrottle = 0;

float distanceCm = -1.0f;

unsigned long lastCommandMs = 0;
unsigned long lastSensorMs = 0;
unsigned long lastTelemetryMs = 0;


float readDistanceCm() {
  digitalWrite(SONAR_TRIG_PIN, LOW);
  delayMicroseconds(3);

  digitalWrite(SONAR_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(SONAR_TRIG_PIN, LOW);

  // Limit blocking time if the sensor is disconnected or has no echo.
  unsigned long duration = pulseIn(SONAR_ECHO_PIN, HIGH, 25000UL);

  if (duration == 0) {
    return -1.0f;
  }

  float cm = duration * 0.0343f / 2.0f;

  if (cm < 2.0f || cm > MAX_DISTANCE_CM) {
    return -1.0f;
  }

  return cm;
}


void stopMotor() {
  analogWrite(MOTOR_EN_PIN, 0);
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, LOW);
}


void applyMotorCommand() {
  const unsigned long now = millis();

  const bool commandFresh =
      (now - lastCommandMs) <= COMMAND_TIMEOUT_MS;

  const bool sensorFresh =
      (now - lastSensorMs) <= SENSOR_TIMEOUT_MS;

  const bool sensorSafe =
      sensorFresh &&
      distanceCm >= MIN_DISTANCE_CM &&
      distanceCm <= MAX_DISTANCE_CM;

  // Fail safe: stop if the command is stale, the sensor is unsafe,
  // or the requested throttle is zero.
  if (!commandFresh || !sensorSafe || requestedThrottle <= 0) {
    stopMotor();
    return;
  }

  // Forward-only motor control.
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, LOW);

  analogWrite(
      MOTOR_EN_PIN,
      constrain(requestedThrottle, 0, 255)
  );
}


void processCommand(const char *line) {
  int steering = 90;
  int throttle = 0;

  if (sscanf(line, "C,%d,%d", &steering, &throttle) == 2) {
    requestedSteeringDeg = constrain(steering, 55, 125);
    requestedThrottle = constrain(throttle, 0, 255);

    steeringServo.write(requestedSteeringDeg);
    lastCommandMs = millis();
  }
}


void readSerialCommands() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputIndex > 0) {
        inputLine[inputIndex] = '\0';
        processCommand(inputLine);
        inputIndex = 0;
      }
    } else if (inputIndex < sizeof(inputLine) - 1) {
      inputLine[inputIndex++] = c;
    } else {
      // Discard an overlong or corrupted packet.
      inputIndex = 0;
    }
  }
}


void setup() {
  pinMode(MOTOR_EN_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  pinMode(SONAR_TRIG_PIN, OUTPUT);
  pinMode(SONAR_ECHO_PIN, INPUT);

  digitalWrite(SONAR_TRIG_PIN, LOW);
  stopMotor();

  steeringServo.attach(STEERING_SERVO_PIN);
  steeringServo.write(requestedSteeringDeg);

  Serial.begin(SERIAL_BAUD);

  lastCommandMs = millis();
  lastSensorMs = 0;
}


void loop() {
  readSerialCommands();

  unsigned long now = millis();

  if (now - lastSensorMs >= SENSOR_INTERVAL_MS) {
    distanceCm = readDistanceCm();
    lastSensorMs = millis();
  }

  applyMotorCommand();

  now = millis();

  if (now - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    Serial.print("S,");
    Serial.println(distanceCm, 1);
    lastTelemetryMs = now;
  }
}
