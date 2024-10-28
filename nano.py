from bluepy import btle  # Import the Bluetooth Low Energy (BLE) library for device communication
import time  # Import time for potential delays
from gpiozero import PWMLED  # Import PWMLED for LED brightness control
import RPi.GPIO  # Import RPi.GPIO to configure the Raspberry Pi pin mode

# Set up GPIO mode for the Raspberry Pi
RPi.GPIO.setmode(RPi.GPIO.BOARD)

# Initialize LED at GPIO pin 18 for PWM control (adjusts brightness)
blue_led = PWMLED(18)

def map_lux_to_analog_value(lux, max_lux=1500):
    """
    Maps a light level in lux to an analog value suitable for PWM control.
    lux: The measured lux value (from sensor)
    max_lux: The maximum lux expected (default 1500)
    Returns: Analog value between 0 and 255 based on lux level.
    """
    analog_value = int((lux / max_lux) * 255)  # Map lux (0 to max_lux) to (0 to 255)
    
    # Ensure the analog_value is clamped between 0 and 255
    analog_value = max(0, min(255, analog_value))
    
    return analog_value

def connect_and_read_ble(device_mac, characteristic_uuid):
    """
    Connects to a BLE device and reads light sensor data, adjusting LED brightness.
    device_mac: MAC address of the BLE device
    characteristic_uuid: UUID of the characteristic to read data from
    """
    try:
        # Attempt to connect to the BLE device
        print(f"Connecting to {device_mac}...")
        device = btle.Peripheral(device_mac, btle.ADDR_TYPE_PUBLIC)

        # Continuously read light sensor values and map them to LED brightness
        while True:
            print(f"Reading characteristic {characteristic_uuid}...")

            # Fetch characteristic by UUID and read its current value
            characteristic = device.getCharacteristics(uuid=characteristic_uuid)[0]
            value = characteristic.read()  # Read the value as bytes
            number = int.from_bytes(value, byteorder='big')  # Convert byte value to an integer
            
            print(f"Value: {number}")  # Output the raw lux reading

            # Convert the lux value to an analog value for LED control
            analog_value = map_lux_to_analog_value(number, 150)
            print(f"Analog Value: {analog_value}")

            # Set the LED brightness (1 - value to invert the scale)
            blue_led.value = 1 - (analog_value / 255)

    except Exception as e:
        # Handle connection or read errors
        print(f"Failed to connect or read from {device_mac}: {str(e)}")
        device.disconnect()
        print("Disconnected")

    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C) to safely disconnect
        print("Disconnecting...")
        device.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    # Define BLE device MAC address and characteristic UUID for light sensor
    device_mac_address = "D3:72:9F:4C:11:67"  
    characteristic_uuid = "2A6E"  

    # Start the BLE connection and LED brightness control
    connect_and_read_ble(device_mac_address, characteristic_uuid)
