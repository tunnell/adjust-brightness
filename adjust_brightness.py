#!/usr/bin/env python3

"""
Ambient Light-Based Screen Brightness Adjuster

This script dynamically adjusts the screen brightness of a laptop based on ambient light sensor readings.
The brightness scales smoothly between a minimum and maximum lux level, reaching 1% at the minimum lux level
and 100% at the maximum lux level. The script supports various options to control verbosity, brightness bar width,
and sleep durations between adjustments.

Features:
- Smooth, incremental brightness adjustments.
- Configurable minimum and maximum lux levels for brightness scaling.
- Adjustable display width for the brightness progress bar.
- Customizable sleep times for different states (when brightness changes or remains the same).
- Logging options for verbosity control.

Dependencies:
1. Python 3: Required to run the script.
2. brightnessctl: A utility to control screen brightness.
3. Ambient light sensor: Typically available on some laptops. Default sensor path is `/sys/bus/iio/devices/iio:device0/in_illuminance_raw`.

Usage:
1. Make the script executable:
   chmod +x adjust_brightness.py
2. Run the script:
   ./adjust_brightness.py [OPTIONS]

Example:
   ./adjust_brightness.py -v --max-lux 400 --min-lux 5 --max-width 30 --short-sleep 0.05 --long-sleep 2

Options:
   -v, --verbose            Enable verbose output (set log level to DEBUG).
   -q, --quiet              Quiet mode (set log level to ERROR).
   --max-lux                Maximum lux level to reach 100% brightness (default: 300).
   --min-lux                Minimum lux level to maintain at least 1% brightness (default: 1).
   --max-width              Width of the brightness display bar (default: 25 characters).
   --short-sleep            Sleep time in seconds when an adjustment is made (default: 0.1).
   --long-sleep             Sleep time in seconds when no adjustment is made (default: 1.0).

GPLv3, CDTunnell, 2024-10-30
"""

import os
import time
import logging
import argparse
from datetime import datetime

def parse_args():
    """
    Parses command-line arguments for configuring the script.

    Returns:
        argparse.Namespace: Parsed arguments with configurable parameters for max lux, min lux, sleep times, etc.
    """
    parser = argparse.ArgumentParser(description="Adjust screen brightness based on ambient light.")

    # Verbose and Quiet flags to adjust logging levels
    parser.add_argument(
        "-v", "--verbose",
        action="store_const", dest="log_level", const=logging.DEBUG,
        help="Enable verbose output (set log level to DEBUG)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_const", dest="log_level", const=logging.ERROR,
        help="Quiet mode (set log level to ERROR)"
    )

    # Default log level if neither -v nor -q is provided
    parser.set_defaults(log_level=logging.INFO)

    # Additional configuration options
    parser.add_argument(
        "--max-lux",
        type=int,
        default=300,
        help="Maximum lux level to reach 100%% brightness (default: 300)"
    )
    parser.add_argument(
        "--min-lux",
        type=int,
        default=1,
        help="Minimum lux level to maintain at least 1%% brightness (default: 1)"
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=25,
        help="Width of the brightness display bar (default: 25 characters)"
    )
    parser.add_argument(
        "--short-sleep",
        type=float,
        default=0.1,
        help="Sleep time in seconds when an adjustment is made (default: 0.1)"
    )
    parser.add_argument(
        "--long-sleep",
        type=float,
        default=1.0,
        help="Sleep time in seconds when no adjustment is made (default: 1.0)"
    )
    return parser.parse_args()

def configure_logging(log_level):
    """
    Configures the logging level for the script.

    Args:
        log_level (int): The logging level to set (e.g., DEBUG, INFO, ERROR).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    return logger

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
    Sets the brightness to the specified target percentage using brightnessctl.

    Args:
        target_brightness (int): The target brightness level to set (0-100).
    """
    os.system(f"brightnessctl s {target_brightness}% > /dev/null 2>&1")

def update_display(brightness_level, target_brightness, lux, max_width, logger):
    """
    Logs the brightness level and other information as a progress bar at the INFO level.

    Args:
        brightness_level (int): Current brightness level as a percentage.
        target_brightness (int): Target brightness level as a percentage.
        lux (int): Current ambient light level in lux.
        max_width (int): Width of the brightness display bar.
        logger (logging.Logger): Logger instance for output control.
    """
    num_hashes = (brightness_level * max_width) // 100
    bar = f"[{'#' * num_hashes}{' ' * (max_width - num_hashes)}] {brightness_level:3}%"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{current_time} | Brightness: {brightness_level:3}% | Target: {target_brightness:3}% | Lux: {lux:5} | {bar}"
    logger.info(message)

def adjust_brightness_step(target_brightness, lux, max_width, logger):
    """
    Adjusts brightness by one step toward the target brightness.

    Args:
        target_brightness (int): Target brightness level (0-100).
        lux (int): Current ambient light level in lux.
        max_width (int): Width of the brightness display bar.
        logger (logging.Logger): Logger instance for output control.

    Returns:
        bool: True if adjustment was made, False if already at target.
    """
    current_brightness = get_brightness()
    if current_brightness == target_brightness:
        logger.debug("Brightness is already at target.")
        return False

    # Adjust by one step toward the target brightness
    step = 1 if target_brightness > current_brightness else -1
    current_brightness += step
    set_brightness(current_brightness)
    update_display(current_brightness, target_brightness, lux, max_width, logger)
    return True

def read_ambient_light(sensor_path, logger):
    """
    Reads the ambient light level from the light sensor.

    Args:
        sensor_path (str): The file path to the ambient light sensor data.
        logger (logging.Logger): Logger instance for output control.

    Returns:
        int: The ambient light level (lux).

    Raises:
        Exception: If the sensor file is missing or contains invalid data.
    """
    try:
        with open(sensor_path, 'r') as sensor_file:
            lux = int(sensor_file.read().strip())
            logger.debug(f"Read ambient light level: {lux} lux")
            return lux
    except (FileNotFoundError, ValueError):
        logger.warning("Warning: Ambient light sensor reading failed.")
        raise

def calculate_target_brightness(lux, max_lux, min_lux):
    """
    Calculates the target brightness based on the ambient light level (lux).

    Args:
        lux (int): The ambient light level (lux).
        max_lux (int): The maximum expected lux value for scaling.
        min_lux (int): The minimum lux level to maintain at least 1% brightness.

    Returns:
        int: The target brightness percentage (1-100).
    """
    if lux >= max_lux:
        return 100
    return max(min_lux, (lux * 100) // max_lux)

def main():
    args = parse_args()
    logger = configure_logging(args.log_level)

    # Path to ambient light sensor data
    sensor_path = "/sys/bus/iio/devices/iio:device0/in_illuminance_raw"

    while True:
        try:
            lux = read_ambient_light(sensor_path, logger)
            target_brightness = calculate_target_brightness(lux, args.max_lux, args.min_lux)
            logger.debug(f"Calculated target brightness: {target_brightness}%")
        except Exception:
            time.sleep(args.long_sleep)
            continue

        # Adjust brightness and determine sleep duration based on adjustment status
        adjusted = adjust_brightness_step(target_brightness, lux, args.max_width, logger)
        sleep_duration = args.short_sleep if adjusted else args.long_sleep
        logger.debug(f"Sleeping for {sleep_duration} seconds")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
