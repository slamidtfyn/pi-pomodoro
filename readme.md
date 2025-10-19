# Pi Pomodoro Timer

Turn your **Raspberry Pi Zero 2 W** into a configurable **Pomodoro timer** using all LEDs on a compatible LED interface (original project uses a Touch pHAT).

* **All LEDs (Back, A, B, C, D, Enter)** indicate active Pomodoro sessions via a rolling fade effect.
* **Enter button** starts/stops the timer loop.
* **Back button** resets the timer to the initial state (all LEDs on, waiting to start).

## Features

* Configurable **work/wait durations** (default 5 min wait / 1 min effect)
* Dynamic rolling LED fade shows active Pomodoro sessions
* Short **“I’m ready” sequence** confirms timer start
* Automatically starts on Raspberry Pi boot

## How it Works as a Pomodoro Timer

1. **Initial state:**

   * All LEDs (Back, A, B, C, D, Enter) are on.
   * Waiting for **Enter** to start a Pomodoro session.

2. **Press Enter:**

   * Short “I’m ready” LED fade runs (~few seconds)
   * Wait timer begins (**configurable via WAIT_MIN**)
   * After wait timer expires, rolling fade runs for the effect duration (**configurable via EFFECT_MIN**)
   * The cycle repeats until **Enter** is pressed again to stop.

3. **Press Back at any time:**

   * Immediately resets to initial state
   * All LEDs on
   * Waiting for Enter to start a new Pomodoro session

> Tip: Adjust **WAIT_MIN** and **EFFECT_MIN** to match your preferred Pomodoro intervals (e.g., 25/5 minutes).

## Requirements

* Raspberry Pi Zero 2 W
* Micro SD card (8GB+)
* **Touch pHAT or any compatible LED/button interface** (this project was tested with Touch pHAT)
* USB keyboard for initial setup (optional)
* Internet access for Raspberry Pi setup

---

## LED Layout Diagram

```
+-----------------+
|  LEDs / Buttons |
+-----------------+
| Back    Enter   |
| A   B   C   D   |
+-----------------+
```

* **Enter:** Start / stop Pomodoro loop
* **Back:** Reset timer to initial state
* **A, B, C, D:** Show rolling fade during active Pomodoro periods
* **All LEDs** are on initially to indicate ready state

## Step 1: Flash Raspberry Pi OS

1. Download **Raspberry Pi OS Lite** (no desktop) from [Raspberry Pi Downloads](https://www.raspberrypi.com/software/).
2. Flash OS to microSD card using **Raspberry Pi Imager** or **balenaEtcher**.
3. Enable SSH by creating an empty file called `ssh` in the boot partition.
4. Configure Wi-Fi (optional) by creating `wpa_supplicant.conf` in boot partition:

```conf
country=DK
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
network={
    ssid="YOUR_WIFI_SSID"
    psk="YOUR_WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
```

## Step 2: Boot & SSH

1. Insert microSD card, power on Pi.
2. SSH into the Pi:

```bash
ssh pi@raspberrypi.local
# default password: raspberry
```

3. Update system:

```bash
sudo apt update
sudo apt upgrade -y
```

## Step 3: Install Dependencies

1. Install system dependencies:

```bash
sudo apt update
sudo apt install python3-pip python3-smbus i2c-tools -y
sudo raspi-config   # Enable I2C: Interface Options → I2C → Enable
sudo reboot
```

2. Install Python dependencies from `requirements.txt`:

```bash
cd /home/pi/pi_pomodoro/
pip3 install -r requirements.txt
```

## Step 4: Connect LEDs

* Connect all LEDs and buttons to GPIO pins using a compatible interface (Touch pHAT recommended).
* All LEDs (Back, A, B, C, D, Enter) are used for Pomodoro timer effects.

## Step 5: Place Script & Configure

1. Place `pi_pomodoro_timer.py` in `/home/pi/pi_pomodoro/`
2. Make it executable:

```bash
chmod +x /home/pi/pi_pomodoro/pi_pomodoro_timer.py
```

3. Configure **Pomodoro durations** (minutes):

* **Command line:** `python3 pi_pomodoro_timer.py 25 5` → 25 min wait / 5 min effect
* **Environment variables:**

```bash
export WAIT_MIN=25
export EFFECT_MIN=5
```

* **Default values:** 5/1 min

## Step 6: Run Script on Boot

1. Create a systemd service:

```bash
sudo nano /etc/systemd/system/pi_pomodoro.service
```

2. Add content:

```ini
[Unit]
Description=Pi Pomodoro Timer
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/pi_pomodoro/pi_pomodoro_timer.py
WorkingDirectory=/home/pi/pi_pomodoro
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pi_pomodoro.service
sudo systemctl start pi_pomodoro.service
sudo systemctl status pi_pomodoro.service
```

## Step 7: Usage

* **Enter:** Start/stop Pomodoro loop
* **Back:** Reset timer to initial state
* LEDs (Back, A, B, C, D, Enter) show dynamic rolling fade effect during active Pomodoro periods

## Notes

* Supports **minutes-based configuration** via CLI args or environment variables.
* Automatic startup ensures the Pi is always ready as a Pomodoro device.
* **A Touch pHAT or compatible LED/button interface is required** for full functionality.

## Troubleshooting & Logging

### 1. View Logs in Real Time

All messages from the Pomodoro script are logged using Python’s `logging` module. To see logs live:

```bash
journalctl -u pi_pomodoro.service -f
```

* `-f` → follow logs in real time
* You will see timestamps, log levels, and messages (e.g., when Enter or Back is pressed, when wait/effect periods start)

### 2. Service Won’t Start

* Ensure the **user** in your service file matches your Pi user (`sla` in your setup).
* Reload systemd after changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart pi_pomodoro.service
```

* Check service status and logs:

```bash
sudo systemctl status pi_pomodoro.service
journalctl -u pi_pomodoro.service -b
```

### 3. LEDs Don’t Light or Fade

* Make sure the user is in `gpio` and `i2c` groups:

```bash
sudo usermod -aG gpio,i2c sla
```

* Enable I2C in `raspi-config`:

```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

* Confirm all LEDs/buttons are connected and working.

### 4. Script Doesn’t Respond to Buttons

* Verify the correct LED/button pins are used for Enter and Back.
* Make sure no other process is using the I2C bus.

### 5. Adjusting Pomodoro Times

* Configure durations via **CLI arguments**, **environment variables**, or defaults in minutes:

```bash
python3 pi_pomodoro_timer.py 25 5
export WAIT_MIN=25
export EFFECT_MIN=5
```

### 6. Debugging Notes

* Logs provide insights on:

  * When Enter/Back are pressed
  * “I’m ready” sequence start
  * Wait and effect periods
* Use `journalctl` to confirm the timer loop is running and LED effects are triggered as expected.