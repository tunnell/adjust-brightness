# Ambient Light-Based Screen Brightness Adjuster

This script adjusts the screen brightness of a laptop based on ambient light sensor readings. It scales brightness smoothly from 1% to 100% depending on the current lux level detected by the sensor. Ideal for devices with ambient light sensors, such as certain laptops.

## Features
- Smooth 1% incremental brightness adjustments.
- Minimum brightness of 1% to prevent the screen from going completely dark.
- Log updates with timestamped ambient light levels and brightness changes.

## Dependencies
1. **Python 3** - for running the script.
2. **brightnessctl** - for controlling screen brightness.
3. **Ambient light sensor** - available via the system’s file structure (`/sys/bus/iio/devices/iio:device0/in_illuminance_raw` by default).

## Installation

### Step 1: Install Python 3
Arch Linux typically includes Python 3 by default. To confirm, run:
```bash
python3 --version
```
If Python 3 is not installed, you can install it using:
```bash
sudo pacman -S python
```

### Step 2: Install brightnessctl
`brightnessctl` is a lightweight utility to manage brightness for backlights and LEDs. Install it with:
```bash
sudo pacman -S brightnessctl
```

### Step 3: Check Ambient Light Sensor
Ensure your device has an ambient light sensor available at `/sys/bus/iio/devices/iio:device0/in_illuminance_raw`. You can check for this file with:
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
3. **Run the script**:
   ```bash
   ./adjust_brightness.py
   ```

The script will begin running in the terminal, adjusting the screen brightness based on ambient light detected. It outputs log lines with timestamps showing the current ambient light, target brightness, and current brightness.

### Optional: Run Script on Startup
To have the script run automatically when the system starts, you can add it to your startup applications:
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
