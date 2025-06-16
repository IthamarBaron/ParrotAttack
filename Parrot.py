import multiprocessing
import os
import ctypes
import subprocess
import threading
import time
import random
from ctypes import wintypes

import tools


def jitter_window_randomly(hwnd, duration=10):
    """
    Moves the given window to random positions across all screens with jittery motion.
    Runs for `duration` seconds.
    """

    user32 = ctypes.windll.user32

    # Get virtual screen bounds (covers all monitors)
    virtual_left   = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
    virtual_top    = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
    virtual_width  = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
    virtual_height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN


    end_time = time.time() + duration
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    window_width = rect.right - rect.left
    window_height = rect.bottom - rect.top

    while (time.time() < end_time) or duration <0:
        # Choose a base random position
        x = random.randint(virtual_left, virtual_left + virtual_width - window_width)
        y = random.randint(virtual_top, virtual_top + virtual_height - window_height)

        # Animate toward that point with jitter
        for _ in range(random.randint(3, 7)):
            jitter_x = x + random.randint(-10, 10)
            jitter_y = y + random.randint(-10, 10)
            user32.MoveWindow(hwnd, jitter_x, jitter_y, window_width, window_height, True)
            time.sleep(random.uniform(0.02, 0.1))

    # Optional: return to top-left after
    # user32.MoveWindow(hwnd, virtual_left, virtual_top, window_width, window_height, True)

def launch_parrot():
    thread_id = threading.get_ident()
    title = f"{thread_id}"
    subprocess.Popen(
        ['cmd.exe', '/k', f'title {title} & curl parrot.live'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print(f"[Thread {thread_id}] Launched parrot with title '{title}'")

    # Function to enumerate windows and find by partial title. WHY IS GETTING A HANDLER SO DAMN COMPLICATED?!?!?! ITS 3AM OMG
    def enum_window_callback(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
                window_title = buffer.value
                if str(thread_id) in window_title and "curl" in window_title:
                    found_windows.append((hwnd, window_title))
        return True

    # Wait and search for the window
    found_windows = []
    max_attempts = 10

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_proc = EnumWindowsProc(enum_window_callback)

    # Search for the window by title over several attempts
    max_attempts = 10
    for _ in range(max_attempts):
        time.sleep(0.5)
        found_windows.clear()
        ctypes.windll.user32.EnumWindows(enum_proc, 0)
        if found_windows:
            break

    # If found, resize the window to 550x400
    if found_windows:
        hwnd, _ = found_windows[0]
        ctypes.windll.user32.MoveWindow(hwnd, 100, 100, 510, 430, True)
        time.sleep(1)
        jitter_window_randomly(hwnd,-1)
    else:
        print("COULDNT FOUND HANDEL FOR WINDOW")


# === Configuration ===
KILL_TIME = 10  # seconds
CHECK_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "perfc.dat")
THREADS_PER_PROC = 12  # Threads per process

# Thread wrapper with shutdown support
def threaded_worker(stop_event):
    while not stop_event.is_set():
        try:
            launch_parrot()
        except Exception:
            pass

# Process function
def parrot_process(stop_event):
    threads = []
    for _ in range(THREADS_PER_PROC):
        t = threading.Thread(target=threaded_worker, args=(stop_event,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

# Monitor for time/file-based killswitches
def monitor_and_control(processes, stop_event):
    start_time = time.time()
    try:
        while True:
            if time.time() - start_time > KILL_TIME:
                print("[KILLSWITCH] Time limit reached.")
                break
            if os.path.exists(CHECK_FILE):
                print(f"[KILLSWITCH] File {CHECK_FILE} detected.")
                break
            time.sleep(0.2)
    finally:
        stop_event.set()
        for p in processes:
            if p.is_alive():
                p.terminate()
        tools.close_parrot_windows()
        print("[SHUTDOWN] All processes terminated.")


if __name__ == '__main__':
    multiprocessing.freeze_support()

    cpu_count = multiprocessing.cpu_count()
    stop_event = multiprocessing.Event()

    processes = []
    for _ in range(cpu_count - 1):
        p = multiprocessing.Process(target=parrot_process, args=(stop_event,))
        p.start()
        processes.append(p)

    monitor_and_control(processes, stop_event)
