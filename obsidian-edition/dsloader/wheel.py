"""The mouse wheel, for the combat log's panel in the game (combatlog.py).

DOSBox 0.74 (GOG's) never passes the wheel on to the game, so the Loader listens for it itself:
a low-level mouse hook (Windows' WH_MOUSE_LL, on a thread of its own with its message loop) counts
the notches turned while DOSBox's window is in front, for the dice log to scroll the panel by
when the game's pointer is over it. The hook only listens: the wheel goes on to DOSBox as ever.
Elsewhere than Windows there is no hook (take() is always 0).
"""

import sys
import threading
from typing import Optional

WHEEL_DELTA = 120  # a notch


class WheelHook:
    def __init__(self, pid: Optional[int]):
        self.pid = pid  # DOSBox's: the wheel counts only with its window in front
        self._notches = 0
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._thread_id = 0  # (the hook thread's, for stop() to end its message loop)
        self._stopping = threading.Event()
        if sys.platform == "win32":
            self._thread = threading.Thread(target=self._run, name="wheel hook", daemon=True)
            self._thread.start()

    def take(self) -> int:
        """The notches turned since the last call: up (away from you) positive."""
        with self._lock:
            n, self._notches = self._notches, 0
        return n

    def stop(self) -> None:
        """The hook taken off: its thread's message loop ends, and with it the hook (a dice log
        closed, as at a reconnect or a new game, leaves no hook behind)."""
        self._stopping.set()
        if self._thread is None or not self._thread_id:
            return  # (not hooked yet: the thread sees _stopping and doesn't wait)
        import ctypes
        WM_QUIT = 0x0012
        ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def _add(self, notches: int) -> None:
        with self._lock:
            self._notches += notches

    def _run(self) -> None:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        LRESULT = ctypes.c_ssize_t
        HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        class MSLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
        user32.SetWindowsHookExW.restype = wintypes.HHOOK
        user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallNextHookEx.restype = LRESULT
        user32.GetForegroundWindow.restype = wintypes.HWND
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        WH_MOUSE_LL, WM_MOUSEWHEEL = 14, 0x020A

        def in_front() -> bool:
            if self.pid is None:
                return True
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
            return pid.value == self.pid

        def proc(code, wparam, lparam):
            try:
                if code == 0 and wparam == WM_MOUSEWHEEL and in_front():
                    data = ctypes.cast(lparam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents.mouseData
                    delta = ctypes.c_short(data >> 16).value
                    if delta:  # (a fine-grained wheel's part of a notch counts as one)
                        self._add(int(delta / WHEEL_DELTA) or (1 if delta > 0 else -1))
            except Exception:  # (never in the way of the mouse)
                pass
            return user32.CallNextHookEx(None, code, wparam, lparam)

        self._proc = HOOKPROC(proc)  # (kept: the hook calls it for as long as it is set)
        hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._proc, kernel32.GetModuleHandleW(None), 0)
        if not hook:
            return
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
        msg = wintypes.MSG()
        PM_NOREMOVE = 0
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_NOREMOVE)  # (the thread's message queue made
        self._thread_id = kernel32.GetCurrentThreadId()  # before stop() can post to it: else its WM_QUIT is lost)
        try:
            while not self._stopping.is_set() and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:  # (stop()'s WM_QUIT ends it)
                pass
        finally:
            user32.UnhookWindowsHookEx(hook)
