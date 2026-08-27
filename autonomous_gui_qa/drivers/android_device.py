"""
Android Device / Emulator Driver using adb.
"""

import os
import subprocess
import time
from typing import Optional, Tuple
from .base import BaseDeviceDriver

class AndroidDeviceDriver(BaseDeviceDriver):
    """Automates Android devices and emulators via ADB."""

    def __init__(self, device_serial: Optional[str] = None, output_dir: str = "/tmp/gui_agent_captures_android"):
        self.serial = device_serial
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.screen_size: Optional[Tuple[int, int]] = None

    def _adb_cmd(self, cmd: str) -> str:
        prefix = f"adb -s {self.serial} " if self.serial else "adb "
        res = subprocess.run(prefix + cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()

    def get_screen_size(self) -> Tuple[int, int]:
        if not self.screen_size:
            out = self._adb_cmd("shell wm size")
            # Output: Physical size: 1080x2400
            dims = out.split(":")[-1].strip().split("x")
            self.screen_size = (int(dims[0]), int(dims[1]))
        return self.screen_size

    def tap(self, norm_x: int, norm_y: int) -> None:
        w, h = self.get_screen_size()
        real_x = int(w * (norm_x / 1000.0))
        real_y = int(h * (norm_y / 1000.0))
        self._adb_cmd(f"shell input tap {real_x} {real_y}")
        time.sleep(0.5)

    def type_text(self, text: str) -> None:
        escaped = text.replace(" ", "%s")
        self._adb_cmd(f"shell input text \"{escaped}\"")
        time.sleep(0.5)

    def swipe(self, direction: str) -> None:
        w, h = self.get_screen_size()
        cx, cy = int(w * 0.5), int(h * 0.5)
        dx, dy = 0, 0
        if direction.upper() == "UP":
            dy = -int(h * 0.3)
        elif direction.upper() == "DOWN":
            dy = int(h * 0.3)
        elif direction.upper() == "LEFT":
            dx = -int(w * 0.3)
        elif direction.upper() == "RIGHT":
            dx = int(w * 0.3)
        self._adb_cmd(f"shell input swipe {cx} {cy} {cx + dx} {cy + dy} 300")
        time.sleep(0.8)

    def press_back(self) -> None:
        self._adb_cmd("shell input keyevent 4")
        time.sleep(0.5)

    def take_screenshot(self, output_filename: str) -> str:
        local_path = os.path.join(self.output_dir, output_filename)
        self._adb_cmd("shell screencap -p /sdcard/temp_screen.png")
        self._adb_cmd(f"pull /sdcard/temp_screen.png \"{local_path}\"")
        return local_path

    def set_appearance(self, mode: str) -> None:
        val = "yes" if mode.lower() == "dark" else "no"
        self._adb_cmd(f"shell "cmd uimode night {val}"")
