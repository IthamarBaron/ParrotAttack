import ctypes
from ctypes import wintypes

#CLOSES ANY WINDOW THAT HAS "curl parrot.live" in its title! EVEN A CHROME WINDOW! (I was lazy)
def close_parrot_windows():
    """
    Find and close all windows with titles containing 'curl parrot.live'
    """
    user32 = ctypes.windll.user32
    found_windows = []

    def enum_window_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                window_title = buffer.value

                # Check if window title contains "curl" and "parrot"
                if "curl" in window_title.lower() and "parrot" in window_title.lower():
                    found_windows.append((hwnd, window_title))
                    print(f"DEBUG: Found matching window: '{window_title}'")
        return True

    # Set up the callback function
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_proc = EnumWindowsProc(enum_window_callback)

    # Find all parrot windows
    print("Searching for windows...")
    user32.EnumWindows(enum_proc, 0)

    print(f"Found {len(found_windows)} parrot windows. Closing them...")

    # Close all found windows
    for hwnd, title in found_windows:
        try:
            # Get process ID and terminate the process
            process_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

            if process_id.value:
                kernel32 = ctypes.windll.kernel32
                PROCESS_TERMINATE = 0x0001
                process_handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, process_id.value)
                if process_handle:
                    kernel32.TerminateProcess(process_handle, 0)
                    kernel32.CloseHandle(process_handle)
                    print(f"Closed: {title}")
        except Exception as e:
            print(f"Error closing {title}: {e}")

    print("Done!")


if __name__ == "__main__":
    close_parrot_windows()