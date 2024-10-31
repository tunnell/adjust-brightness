#!/usr/bin/env python3

"""
This script adjusts the brightness of a laptop screen based on ambient light sensor readings.
It reads data from a specified ambient light sensor, calculates the appropriate target brightness
(based on lux levels), and adjusts the screen brightness using `brightnessctl`. The brightness 
adjustment is done smoothly, 1% at a time, and the screen brightness will never go below 1%.

Dependencies:
- brightnessctl: A utility to read and control device brightness
- Ambient light sensor available via the file system

The script runs continuously, adjusting the brightness every second.

GPLv3, CDTunnell 2024-10-30
"""

import os
import time
from datetime import datetime

def get_brightness():
    """
    Retrieves the current brightness as a percentage using brightnessctl.

    Returns:
        int: The current brightness level as a percentage (0-100).
    """
    current_brightness = int(os.popen("brightnessctl g").read().strip())
    max_brightness = int(os.popen("brightnessctl m").read().strip())
    
    brightness_percent = (current_brightness * 100) // max_brightness
    return brightness_percent

def set_brightness(target_brightness):
    """
    Sets the brightness to the given target percentage using brightnessctl.

    Args:
        target_brightness (int): The target brightness level to set (0-100).
    """
    os.system(f"brightnessctl s {target_brightness}% > /dev/null 2>&1")

def adjust_brightness(target_brightness, lux):
    """
    Adjusts the brightness smoothly to the target brightness by stepping 1% at a time.

    Args:
        target_brightness (int): The target brightness level to set (0-100).
        lux (int): The current ambient light level in lux for reference in output.
    """
    current_brightness = get_brightness()
    
    # Get current datetime for logging
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Print the current status with datetime
    print(f"{current_time}\tAmbient Light: {lux} lux\tCurrent Brightness: {current_brightness}%\tTarget Brightness: {target_brightness}%")

    # Increase or decrease brightness 1% at a time
    step = 1 if target_brightness > current_brightness else -1

    for brightness in range(current_brightness, target_brightness, step):
        set_brightness(brightness)
        print(".", end="", flush=True)  # Print dot without newline to indicate progress
        time.sleep(0.1)  # Sleep for 100 milliseconds between steps
    
    # Ensure final target is reached
    set_brightness(target_brightness)
    print()  # Newline after finishing the adjustment

def read_ambient_light(sensor_path):
    """
    Reads the ambient light level from the light sensor.

    Args:
        sensor_path (str): The file path to the ambient light sensor data.

    Returns:
        int: The ambient light level (lux).
    """
    try:
        with open(sensor_path, 'r') as sensor_file:
            lux = int(sensor_file.read().strip())
            return lux
    except (FileNotFoundError, ValueError):
        return 0  # Return 0 if the sensor file is missing or invalid

def calculate_target_brightness(lux, max_lux=300):
    """
    Calculates the target brightness based on the ambient light level (lux).

    Args:
        lux (int): The ambient light level (lux).
        max_lux (int): The maximum expected lux value for scaling (default is 300).

    Returns:
        int: The target brightness percentage (1-100), with a minimum brightness of 1%.
    """
    if lux >= max_lux:
        return 100
    return max(1, (lux * 100) // max_lux)  # Minimum brightness of 1%

def main():
    """
    Main function that adjusts the screen brightness based on ambient light sensor data.
    """
    sensor_path = "/sys/bus/iio/devices/iio:device0/in_illuminance_raw"
    
    while True:
        # Read the current ambient light value
        lux = read_ambient_light(sensor_path)
        
        # Calculate the target brightness (with a minimum of 1%)
        target_brightness = calculate_target_brightness(lux)
        
        # Adjust the brightness smoothly and print the current status
        adjust_brightness(target_brightness, lux)
        
        # Sleep for 1 second before checking the light sensor again
        time.sleep(1)

if __name__ == "__main__":
    main()
