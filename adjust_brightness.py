#!/usr/bin/env python3

import os
import time
import logging
import argparse
from datetime import datetime

MAX_WIDTH = 25  # Number of characters in the progress bar
FULL_BAR = 100  # Total percentage width (100%)

def parse_args():
    parser = argparse.ArgumentParser(description="Adjust screen brightness based on ambient light.")
    parser.add_argument(
        "-l", "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    return parser.parse_args()

def configure_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    return logger

def get_brightness():
    current_brightness = int(os.popen("brightnessctl g").read().strip())
    max_brightness = int(os.popen("brightnessctl m").read().strip())
    brightness_percent = (current_brightness * 100) // max_brightness
    return brightness_percent

def set_brightness(target_brightness):
    os.system(f"brightnessctl s {target_brightness}% > /dev/null 2>&1")

def update_display(brightness_level, target_brightness, lux, logger):
    """
    Display the brightness level and other information as a progress bar.
    This is logged at INFO level to be the default visible output.
    """
    num_hashes = (brightness_level * MAX_WIDTH) // FULL_BAR
    bar = f"[{'#' * num_hashes}{' ' * (MAX_WIDTH - num_hashes)}] {brightness_level:3}%"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Using carriage return \r to overwrite the same line in the terminal
    message = f"\r{current_time} | Brightness: {brightness_level:3}% | Target: {target_brightness:3}% | Lux: {lux:5} | {bar}"
    print(message, end="", flush=True)  # Direct print for continuous updating effect

def adjust_brightness_step(target_brightness, lux, logger):
    current_brightness = get_brightness()
    if current_brightness == target_brightness:
        logger.debug("Brightness is already at target.")
        return False

    step = 1 if target_brightness > current_brightness else -1
    current_brightness += step
    set_brightness(current_brightness)
    update_display(current_brightness, target_brightness, lux, logger)
    return True

def read_ambient_light(sensor_path, logger):
    try:
        with open(sensor_path, 'r') as sensor_file:
            lux = int(sensor_file.read().strip())
            logger.debug(f"Read ambient light level: {lux} lux")
            return lux
    except (FileNotFoundError, ValueError):
        logger.warning("Warning: Ambient light sensor reading failed.")
        raise

def calculate_target_brightness(lux, max_lux=300):
    if lux >= max_lux:
        return 100
    return max(1, (lux * 100) // max_lux)

def main():
    args = parse_args()
    logger = configure_logging(args.log_level)

    sensor_path = "/sys/bus/iio/devices/iio:device0/in_illuminance_raw"

    while True:
        try:
            lux = read_ambient_light(sensor_path, logger)
            target_brightness = calculate_target_brightness(lux)
            logger.debug(f"Calculated target brightness: {target_brightness}%")
        except Exception:
            time.sleep(1)
            continue

        adjusted = adjust_brightness_step(target_brightness, lux, logger)
        sleep_duration = 0.1 if adjusted else 1
        logger.debug(f"Sleeping for {sleep_duration} seconds")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
