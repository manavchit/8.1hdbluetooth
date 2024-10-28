#include <ArduinoBLE.h>  // Include library for BLE functionality
#include <BH1750.h>      // Include library for BH1750 light sensor
#include <Wire.h>        // Include library for I2C communication

BH1750 lightMeter;  // Create an instance of the BH1750 light sensor

// Define the BLE service for LED control with a specific UUID
BLEService ledService("180F");

// Define the BLE characteristic for lux readings with a specific UUID and read/write permissions
BLEByteCharacteristic luxCharacteristic("2A6E", BLERead | BLEWrite);

// List of allowed central MAC addresses (only authorized devices can connect)
const String allowedMACs[] = {"D3:72:9F:4C:11:67"};  // Add actual allowed MAC addresses here

void setup() {
  Serial.begin(9600);  // Begin serial communication at 9600 baud rate
  while (!Serial);     // Wait for Serial to initialize
  
  // Begin BLE initialization
  if (!BLE.begin()) {
    Serial.println("Starting Bluetooth® Low Energy failed!");
    while (1);  // Stop execution if BLE initialization fails
  }

  // Set the BLE device's advertised local name and add the service
  BLE.setLocalName("Nano 33 IoT");
  BLE.setAdvertisedService(ledService);

  // Add the lux characteristic to the BLE service
  ledService.addCharacteristic(luxCharacteristic);

  // Add the service to BLE
  BLE.addService(ledService);

  // Set the initial value for the characteristic to 0
  luxCharacteristic.writeValue(0);

  // Start advertising the BLE service to make the device discoverable
  BLE.advertise();
  Serial.println("BLE Peripheral initialized");

  // Initialize I2C for the BH1750 light sensor
  Wire.begin();
  lightMeter.begin();
  Serial.println(F("BH1750 initialized"));
}

void loop() {
  // Listen for any BLE device attempting to connect
  BLEDevice central = BLE.central();

  // Check if a central device has connected
  if (central) {
    String centralMAC = central.address();  // Get the MAC address of the central device
    Serial.print("Trying to connect central: ");
    Serial.println(centralMAC);

    // Check if the connecting central device's MAC address is allowed
    bool isAllowed = false;
    for (int i = 0; i < sizeof(allowedMACs) / sizeof(allowedMACs[0]); i++) {
      if (centralMAC.equalsIgnoreCase(allowedMACs[i])) {
        isAllowed = true;  // Mark as allowed if MAC matches
        break;
      }
    }

    // Proceed if the central device is authorized
    if (isAllowed) {
      Serial.println("Allowed central is detected.");

      // Stay in this loop while the central device remains connected
      while (central.connected()) {
        Serial.print(">> ");
        
        // Read the lux level from the BH1750 sensor
        float lux = lightMeter.readLightLevel();
        Serial.print("Light: ");
        Serial.print(lux);
        Serial.println(" lx");  // Display lux value in the Serial Monitor

        // Delay between each lux reading to avoid overloading BLE communication
        delay(500);

        // Map the lux value to an analog value (0-255) suitable for LED brightness control
        uint8_t analogLux = map(lux, 0, 1500, 0, 255);
        luxCharacteristic.writeValue(analogLux);  // Write the analog lux value to the BLE characteristic
      }

      // Log disconnection when the central device disconnects
      Serial.print(F("Disconnected from central: "));
      Serial.println(central.address());
    } else {
      // Reject unauthorized central device and disconnect it
      Serial.println("Connection rejected. Central not allowed.");
      BLE.disconnect();
    }
  }
}
