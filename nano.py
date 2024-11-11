from bluepy import btle       # Import the BluePy library for Bluetooth Low Energy (BLE) communication
import time                   # Import time module for delays
from gpiozero import Buzzer   # Import GPIOZero library to control the buzzer
import RPi.GPIO               # Import RPi.GPIO for handling GPIO modes and pin configurations on Raspberry Pi

# Set GPIO mode to use physical pin numbering for easy identification
RPi.GPIO.setmode(RPi.GPIO.BOARD)

# Initialize a Buzzer on GPIO pin 18 (use the physical pin number).
# You can change the pin number if needed based on your setup.
buzzer = Buzzer(18)

def map_distance_to_buzz(distance, max_distance=60):
    """
    Maps a given distance to a buzzing pattern to indicate proximity.
    
    Args:
    - distance (int): The distance to an object (in cm) received from the BLE device.
    - max_distance (int): The distance threshold in cm. If the object is closer than this distance,
                          the buzzer will emit short beeps.

    Behavior:
    - If the distance is below the threshold, the buzzer emits short beeps
      to alert the user about close proximity to an object (e.g., a wall).
    - If the distance is greater than or equal to the threshold, the buzzer remains off.
    """
    if distance < max_distance:
        buzzer.on()             # Activate the buzzer to emit a beep
        time.sleep(0.1)         # Hold the buzzer on for a short 0.1 second beep
        buzzer.off()            # Deactivate the buzzer to stop the beep
        time.sleep(0.1)         # Wait for 0.1 seconds before the next beep
    else:
        buzzer.off()            # Ensure the buzzer is off if distance exceeds max_distance

def connect_and_read_ble(device_mac, characteristic_uuid):
    """
    Connect to a BLE device, read distance data continuously, and trigger alerts based on proximity.

    Args:
    - device_mac (str): MAC address of the BLE device to connect to.
    - characteristic_uuid (str): UUID of the characteristic providing distance data.

    Behavior:
    - Establishes a connection to the BLE device using its MAC address.
    - Continuously reads the specified characteristic, which provides the distance value in cm.
    - Converts the received byte data into an integer distance and triggers the `map_distance_to_buzz`
      function to control the buzzer based on proximity.
    """
    try:
        # Attempt connection to the BLE device with provided MAC address
        print(f"Connecting to {device_mac}...")
        device = btle.Peripheral(device_mac, btle.ADDR_TYPE_PUBLIC)  # Establish BLE connection

        # Indicate that the characteristic read process is starting
        print(f"Reading characteristic {characteristic_uuid}...")

        # Start an infinite loop to continuously read and process distance data
        while True:
            # Fetch the BLE characteristic specified by the UUID
            characteristic = device.getCharacteristics(uuid=characteristic_uuid)[0]
            
            # Read the raw data from the characteristic (in bytes)
            value = characteristic.read()
            
            # Convert the byte data to an integer representing the distance in centimeters
            number = int.from_bytes(value, byteorder='big')  
            print(f"Distance from wall: {number} cm")  # Output the distance reading for reference

            # Map the distance to a buzzing pattern, alerting the user if within max_distance
            map_distance_to_buzz(number, max_distance=60)

    except Exception as e:
        # Handle any exceptions during connection or reading
        print(f"Failed to connect or read from {device_mac}: {str(e)}")
        
        # Ensure that the device is disconnected in case of an error
        device.disconnect()
        print("Disconnected")  # Log disconnection status

    except KeyboardInterrupt:
        # If the user interrupts (e.g., pressing Ctrl+C), gracefully disconnect the device
        print("Disconnecting...")
        device.disconnect()     # Ensure clean disconnection from BLE device
        print("Disconnected")

if __name__ == "__main__":
    # Define the BLE device's MAC address and characteristic UUID to identify the source of distance data
    device_mac_address = "D3:72:9F:4C:11:67"  # Replace with actual MAC address of your BLE device
    characteristic_uuid = "2A6E"              # Replace with characteristic UUID for distance data

    # Start the BLE connection and begin reading distance data from the device
    connect_and_read_ble(device_mac_address, characteristic_uuid)
