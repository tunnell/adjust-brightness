# Ambient Light-Based Screen Brightness Adjuster

This script dynamically adjusts the screen brightness of a laptop based on ambient light sensor readings. Brightness scales smoothly between 1% and 100% depending on the current lux level detected by the sensor, making it ideal for devices with ambient light sensors.

## Features
- Smooth 1% incremental brightness adjustments based on ambient light levels.
- Configurable minimum and maximum lux levels to control brightness scaling.
- Customizable display bar width for brightness level.
- Adjustable sleep times for cases when brightness needs or does not need adjustment.
- Flexible logging options with command-line flags for verbosity control.

## Dependencies
1. **Python 3** - Required to run the script.
2. **brightnessctl** - Controls screen brightness.
3. **Ambient light sensor** - Typically available on some laptops. The default sensor path is `/sys/bus/iio/devices/iio:device0/in_illuminance_raw`.

## Installation

### Step 1: Install Python 3
Python 3 is often included by default. To confirm:
```bash
python3 --version
```
If Python 3 is missing, you can install it:
```bash
sudo pacman -S python
```

### Step 2: Install brightnessctl
`brightnessctl` is a utility for managing brightness. Install it with:
```bash
sudo pacman -S brightnessctl
```

### Step 3: Check Ambient Light Sensor
Ensure your device has an ambient light sensor at `/sys/bus/iio/devices/iio:device0/in_illuminance_raw`. Check with:
```bash
ls /sys/bus/iio/devices/iio:device0/in_illuminance_raw
```
If this file does not exist, the script may not work unless you specify the correct sensor path.

## Running the Script

1. **Clone or Download** the script to your local system.
2. **Make the script executable**:
   ```bash
   chmod +x adjust_brightness.py
   ```
3. **Run the script with options as needed**:
   ```bash
   ./adjust_brightness.py [OPTIONS]
   ```

### Command-Line Options

| Option            | Description                                                                                     | Default |
|-------------------|-------------------------------------------------------------------------------------------------|---------|
| `-v`, `--verbose` | Enable verbose output, setting log level to `DEBUG`.                                            | `INFO`  |
| `-q`, `--quiet`   | Quiet mode, setting log level to `ERROR`.                                                       | `INFO`  |
| `--max-lux`       | Maximum lux level to reach 100% brightness.                                                     | `300`   |
| `--min-lux`       | Minimum lux level to maintain at least 1% brightness.                                           | `1`     |
| `--max-width`     | Width of the brightness display bar in characters.                                              | `25`    |
| `--short-sleep`   | Sleep time in seconds when an adjustment is made (recommended to keep this value small).        | `0.1`   |
| `--long-sleep`    | Sleep time in seconds when no adjustment is made (helps save resources).                        | `1.0`   |

### Example Usage

- Default settings:
  ```bash
  ./adjust_brightness.py
  ```
- Verbose output (for debugging):
  ```bash
  ./adjust_brightness.py -v
  ```
- Quiet mode (only error messages shown):
  ```bash
  ./adjust_brightness.py -q
  ```
- Custom brightness scaling and sleep times:
  ```bash
  ./adjust_brightness.py --max-lux 500 --min-lux 10 --short-sleep 0.05 --long-sleep 2
  ```

The script will run in the terminal, adjusting screen brightness based on ambient light. It logs updates with timestamps showing the current ambient light, target brightness, and current brightness level.

### Optional: Run Script on Startup
To have the script run automatically on startup, you can add it as a systemd service:
1. Create a systemd service file, e.g., `/etc/systemd/system/brightness-adjust.service`:
   ```ini
   [Unit]
   Description=Ambient Light-Based Brightness Adjuster

   [Service]
   ExecStart=/path/to/your/adjust_brightness.py
   Restart=always

   [Install]
   WantedBy=default.target
   ```
2. **Enable the service**:
   ```bash
   sudo systemctl enable brightness-adjust.service
   ```
3. **Start the service** immediately:
   ```bash
   sudo systemctl start brightness-adjust.service
   ```

## Troubleshooting
- Ensure your device supports ambient light sensors.
- Confirm the `brightnessctl` commands work manually.
- Run the script with `python3 -u adjust_brightness.py` to observe real-time logging for debugging.

## License
GPLv3, CDTunnell, 2024-10-30
