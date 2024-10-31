#!/usr/bin/env python3

"""
This script adjusts the brightness of a laptop screen based on ambient light sensor readings.
It reads data from a specified ambient light sensor, calculates the appropriate target brightness
(based on lux levels), and adjusts the screen brightness using `brightnessctl`. The brightness
adjustment is done smoothly, with a progress bar displayed as `[####################          ] 80%`,
where each '#' represents 4% of brightness, and the remaining spaces complete the fixed width.

Dependencies:
- brightnessctl: A utility to read and control device brightness
- Ambient light sensor available via the system file structure

The script runs continuously, adjusting brightness based on ambient light, with each update
showing a timestamp, current brightness, target brightness, and lux level.

GPLv3, CDTunnell 2024-10-31
"""

import os
import time
from datetime import datetime

MAX_WIDTH = 25  # Number of characters in the progress bar
FULL_BAR = 100  # Total percentage width (100%)

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

def update_display(brightness_level, target_brightness, lux):
    """
    Updates the progress bar display to show the current brightness level with timestamp.
    Args:
        brightness_level (int): Current brightness level as a percentage.
        target_brightness (int): Target brightness level as a percentage.
        lux (int): Current ambient light level in lux.
    """
    num_hashes = (brightness_level * MAX_WIDTH) // FULL_BAR  # Calculate # based on percentage
    bar = f"[{'#' * num_hashes}{' ' * (MAX_WIDTH - num_hashes)}] {brightness_level:3}%"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\r{current_time} | Brightness: {brightness_level:3}% | Target: {target_brightness:3}% | Lux: {lux:5} | {bar}", end="", flush=True)

def adjust_brightness(target_brightness, lux):
    """
    Smoothly adjusts brightness to the target brightness in increments.
    Args:
        target_brightness (int): Target brightness level (0-100).
        lux (int): Current ambient light level in lux.
    """
    current_brightness = get_brightness()
    step = 1 if target_brightness > current_brightness else -1

    # Loop until we reach the target brightness
    while current_brightness != target_brightness:
        set_brightness(current_brightness)
        update_display(current_brightness, target_brightness, lux)
        current_brightness += step
        time.sleep(0.1)

    # Ensure final target is reached and displayed
    set_brightness(target_brightness)
    update_display(target_brightness, target_brightness, lux)

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
    sensor_path = "/sys/bus/iio/devices/iio:device0/in_illuminance_raw"

    # Initialize previous values to ensure the first loop prints the state
    previous_brightness = None
    previous_target = None
    previous_lux = None

    while True:
        # Read the current ambient light level
        lux = read_ambient_light(sensor_path)

        # Calculate the target brightness based on lux
        target_brightness = calculate_target_brightness(lux)

        # Check if an update is necessary (values have changed)
        current_brightness = get_brightness()
        if (current_brightness != previous_brightness or
            target_brightness != previous_target or
            lux != previous_lux):

            # Adjust brightness to the target level smoothly
            adjust_brightness(target_brightness, lux)

            # Update previous values
            previous_brightness = current_brightness
            previous_target = target_brightness
            previous_lux = lux

        # Sleep for 1 second before checking again
        time.sleep(1)

if __name__ == "__main__":
    main()


