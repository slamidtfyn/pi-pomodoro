#!/usr/bin/env python3
"""
Pi Pomodoro Timer

Uses all LEDs (Back, A, B, C, D, Enter) to show a rolling fade effect.
Enter: Start/Stop loop
Back: Reset to initial state
Configurable WORK and PAUSE times in minutes:
1. Command line args
2. Environment variables
3. Defaults
"""

import touchphat
from time import sleep, time
from threading import Thread, Event
import os
import sys
import logging

# ================= Logging =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger()

# ================= Configuration =================
ALL_LEDS = ["Back", "A", "B", "C", "D", "Enter"]
FADE_STEPS = 10         # Number of steps in fade (more = smoother)
DELAY = 0.02            # Base delay for micro-blinks
LED_OFF_DELAY = 0.01    # Stagger between LEDs for rolling effect

# Default times in minutes
DEFAULT_WORK_MIN = 25
DEFAULT_PAUSE_MIN = 5

# ======== Load configuration (priority) ========
if len(sys.argv) >= 3:
    WORK_MIN = float(sys.argv[1])
    PAUSE_MIN = float(sys.argv[2])
elif os.getenv("WORK_MIN") and os.getenv("PAUSE_MIN"):
    WORK_MIN = float(os.getenv("WORK_MIN"))
    PAUSE_MIN = float(os.getenv("PAUSE_MIN"))
else:
    WORK_MIN = DEFAULT_WORK_MIN
    PAUSE_MIN = DEFAULT_PAUSE_MIN

# Convert minutes to seconds
WORK_TIME = WORK_MIN * 60
PAUSE_TIME = PAUSE_MIN * 60
# ==================================================

# Global state
running = False
stop_event = Event()
first_run = True

# Turn all LEDs on at start
for l in ALL_LEDS:
    touchphat.set_led(l, 1)

# -------- Light sequences --------
def ready_light_sequence():
    """Short 'I'm ready' sequence: fade each LED in and out quickly"""
    for l in ALL_LEDS:
        if stop_event.is_set():
            return
        for _ in range(FADE_STEPS):
            touchphat.set_led(l, 1)
            sleep(DELAY)
            touchphat.set_led(l, 0)
            sleep(DELAY)
        for _ in range(FADE_STEPS):
            touchphat.set_led(l, 1)
            sleep(DELAY)
            touchphat.set_led(l, 0)
            sleep(DELAY)
    for l in ALL_LEDS:
        touchphat.set_led(l, 0)

def dynamic_smooth_fade(duration=1.0):
    """Smooth fade-in/out for each LED with rolling wave effect"""
    step_time = duration / FADE_STEPS
    led_offsets = list(range(len(ALL_LEDS)))  # stagger each LED

    for step in range(1, FADE_STEPS + 1):
        for idx, l in enumerate(ALL_LEDS):
            for _ in range(step):
                if stop_event.is_set():
                    return
                touchphat.set_led(l, 1)
                sleep(DELAY + led_offsets[idx]*LED_OFF_DELAY)
                touchphat.set_led(l, 0)
                sleep(DELAY)
        sleep(step_time)

    for step in range(FADE_STEPS, 0, -1):
        for idx, l in enumerate(ALL_LEDS):
            for _ in range(step):
                if stop_event.is_set():
                    return
                touchphat.set_led(l, 1)
                sleep(DELAY + led_offsets[idx]*LED_OFF_DELAY)
                touchphat.set_led(l, 0)
                sleep(DELAY)
        sleep(step_time)

    for l in ALL_LEDS:
        touchphat.set_led(l, 0)

# -------- Main loop --------
def effect_loop():
    """Main loop: waits WORK_TIME, runs dynamic fade for PAUSE_TIME, repeats until stopped"""
    global first_run
    while running and not stop_event.is_set():
        if first_run:
            logger.info("First Enter press: 'I'm ready' light sequence")
            ready_light_sequence()
            first_run = False

        logger.info(f"Working {WORK_MIN} minutes...")
        for _ in range(int(WORK_TIME)):
            if stop_event.is_set():
                return
            sleep(1)

        if stop_event.is_set():
            return
        logger.info(f"Pause {PAUSE_MIN} minutes dynamic smooth fade effect")
        end_time = time() + PAUSE_TIME
        while time() < end_time and not stop_event.is_set():
            dynamic_smooth_fade(duration=2.0)

# -------- Button handlers --------
def toggle_running():
    """Start or stop the fade loop when Enter is pressed"""
    global running, stop_event, first_run
    if not running:
        running = True
        stop_event.clear()
        first_run = True
        t = Thread(target=effect_loop)
        t.start()
        logger.info("Enter pressed: Loop started")
    else:
        running = False
        stop_event.set()
        for l in ALL_LEDS:
            touchphat.set_led(l, 0)
        logger.info("Enter pressed: Loop stopped, all LEDs off")

def reset_to_initial_state():
    """Reset script to initial state when Back is pressed"""
    global running, stop_event, first_run
    running = False
    stop_event.set()
    first_run = True
    for l in ALL_LEDS:
        touchphat.set_led(l, 1)
    logger.info("Back pressed: Reset to initial state, waiting for Enter...")

# -------- Bind buttons --------
touchphat.on_touch("Enter", lambda _: toggle_running())
touchphat.on_touch("Back", lambda _: reset_to_initial_state())

# -------- Keep script running --------
logger.info(f"All LEDs on. Press Enter to start/stop the loop. WORK={WORK_MIN} min, PAUSE={PAUSE_MIN} min")
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    stop_event.set()
    for l in ALL_LEDS:
        touchphat.set_led(l, 0)
    logger.info("Program terminated, all LEDs off")
