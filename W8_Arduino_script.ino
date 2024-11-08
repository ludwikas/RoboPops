#include <Arduino.h>

// Pin definitions
const int voltagePin = A1;    // Analog pin to read voltage from the robot controller
const int stepPin = 3;        // Digital pin to send step pulses to the stepper motor
const int dirPin = 2;         // Digital pin to control motor direction (manually set)

// Constants for the voltage range and step delay range
const float minVoltage = 0.1;      // Minimum voltage (0.1V to avoid log(0))
const float maxVoltage = 5.0;      // Maximum voltage (5V)
const int maxStepDelay = 10000;     // Maximum delay (slowest speed)
const int minStepDelay = 500;      // Minimum delay (fastest speed)

// Motor configuration
const int stepsPerRevolution = 200;  // Number of steps per revolution for the stepper motor
int stepsToMove = 0;                 // Number of steps to move based on voltage

// Threshold to stop the motor when the voltage is close to 0V
const float stopThreshold = 0.1;   // Voltage below this will stop the motor

// Timer variables for controlling motor pulses and analog reads
unsigned long lastStepTime = 0;        // Last time the motor was stepped
unsigned long lastAnalogReadTime = 0;  // Last time the analog value was read
unsigned long analogReadInterval = 100; // Interval for reading analog input in milliseconds

// Variables
int stepDelay = 0;

void setup() {
  // Initialize pins
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);      // Manually set direction pin
  pinMode(voltagePin, INPUT);

  // Serial for debugging
  Serial.begin(9600);
  
  // Set default motor direction (HIGH for clockwise, LOW for counterclockwise)
  digitalWrite(dirPin, HIGH);   // You can change this to LOW to reverse the direction
}

void loop() {
  // Get current time in milliseconds
  unsigned long currentTime = millis();

  // Read analog value at defined intervals (e.g., every 100 ms)
  if (currentTime - lastAnalogReadTime >= analogReadInterval) {
    lastAnalogReadTime = currentTime;

    // Read the voltage value from the analog pin (0 to 1023)
    int analogValue = analogRead(voltagePin);
    
    // Convert the analog value (0-1023) to voltage (0-5V)
    float voltage = (analogValue / 1023.0) * 5.0;

    // Stop motor if voltage is below the threshold
    if (voltage < stopThreshold) {
      stepDelay = -1;  // Special case: -1 means the motor should stop
      stepsToMove = 0; // No steps to move if voltage is too low
    } else {
      // Logarithmic interpolation to calculate step delay based on voltage
      float logScale = log(voltage + 1); // Shifted to avoid log(0) issues
      float maxLogScale = log(maxVoltage + 1);
      stepDelay = maxStepDelay - (logScale / maxLogScale) * (maxStepDelay - minStepDelay);
      
      // Calculate steps to move based on the voltage value (e.g., assume 1 revolution max at 5V)
      stepsToMove = (voltage / maxVoltage) * stepsPerRevolution;  // Scale steps to move based on voltage
    }

    // Output the step delay, steps to move, and voltage for debugging purposes
    Serial.print("Voltage: ");
    Serial.print(voltage);
    Serial.print(" V, Step Delay: ");
    Serial.print(stepDelay);
    Serial.print(", Steps to Move: ");
    Serial.println(stepsToMove);
  }

  // Step the motor at intervals defined by stepDelay
  if (stepDelay > 0 && stepsToMove > 0) {
    if (currentTime - lastStepTime >= stepDelay / 1000) {  // Convert stepDelay to milliseconds
      lastStepTime = currentTime;

      // Step the motor
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(stepDelay);  // Time between each pulse
      digitalWrite(stepPin, LOW);
      delayMicroseconds(stepDelay);
      
      // Decrease the number of steps left to move
      stepsToMove--;
    }
  } else if (stepDelay == -1) {
    // Motor stopped, no steps will be executed
    Serial.println("Motor stopped.");
  }
}