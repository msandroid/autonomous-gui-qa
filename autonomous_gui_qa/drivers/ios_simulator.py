"""
iOS Simulator Driver using xcrun simctl and AppleScript / System Events.
"""

import os
import subprocess
import time
from typing import Tuple, Optional
from .base import BaseDeviceDriver

class IOSSimulatorDriver(BaseDeviceDriver):
    """Automates iOS Simulator via simctl and native macOS GUI events."""

    def __init__(self, device_udid: str = "booted", bundle_id: Optional[str] = None, output_dir: str = "/tmp/gui_agent_captures"):
        self.device_udid = device_udid
        self.bundle_id = bundle_id
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def boot(self, device_name: str = "iPhone 17 Pro") -> None:
        cmd = f"xcrun simctl bootstatus \"{device_name}\" -b"
        subprocess.run(cmd, shell=True, check=True)
        subprocess.run("open -a Simulator", shell=True, check=True)
        time.sleep(2)

    def launch_app(self, bundle_id: Optional[str] = None) -> None:
        bid = bundle_id or self.bundle_id
        if not bid:
            raise ValueError("No bundle_id specified")
        subprocess.run(f"xcrun simctl launch {self.device_udid} {bid}", shell=True, check=True)
        time.sleep(2)

    def terminate_app(self, bundle_id: Optional[str] = None) -> None:
        bid = bundle_id or self.bundle_id
        if bid:
            subprocess.run(f"xcrun simctl terminate {self.device_udid} {bid}", shell=True)

    def set_appearance(self, mode: str) -> None:
        m = mode.lower()
        if m in ["dark", "light"]:
            subprocess.run(f"xcrun simctl ui {self.device_udid} appearance {m}", shell=True, check=True)
            time.sleep(1)

    def set_clean_status_bar(self) -> None:
        cmd = (
            f"xcrun simctl status_bar {self.device_udid} override "
            "--time 9:41 --dataNetwork wifi --wifiMode active "
            "--wifiBars 3 --cellularMode active --cellularBars 4 "
            "--batteryState charged --batteryLevel 100"
        )
        subprocess.run(cmd, shell=True)

    def take_screenshot(self, output_filename: str) -> str:
        filepath = os.path.join(self.output_dir, output_filename)
        subprocess.run(f"xcrun simctl io {self.device_udid} screenshot \"{filepath}\"", shell=True, check=True)
        return filepath

    def get_window_bounds(self) -> Tuple[int, int, int, int]:
        script = """
        tell application "System Events"
            tell process "Simulator"
                set frontmost to true
                set w to window 1
                set p to position of w
                set s to size of w
                return (item 1 of p) & "," & (item 2 of p) & "," & (item 1 of s) & "," & (item 2 of s)
            end tell
        end tell
        """
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=True)
        parts = [int(x.strip()) for x in res.stdout.strip().split(",")]
        return parts[0], parts[1], parts[2], parts[3]

    def tap(self, norm_x: int, norm_y: int) -> None:
        wx, wy, ww, wh = self.get_window_bounds()
        titlebar_offset = 32
        device_h = wh - titlebar_offset
        screen_x = wx + int(ww * (norm_x / 1000.0))
        screen_y = wy + titlebar_offset + int(device_h * (norm_y / 1000.0))

        script = f"""
        tell application "Simulator" to activate
        tell application "System Events"
            click at {{{screen_x}, {screen_y}}}
        end tell
        """
        subprocess.run(["osascript", "-e", script], capture_output=True)
        time.sleep(0.5)

    def type_text(self, text: str) -> None:
        safe_text = text.replace("\\", "\\\\").replace("\"", "\\\"")
        script = f"""
        tell application "Simulator" to activate
        tell application "System Events"
            keystroke \"{safe_text}\"
        end tell
        """
        subprocess.run(["osascript", "-e", script], capture_output=True)
        time.sleep(0.5)

    def swipe(self, direction: str) -> None:
        wx, wy, ww, wh = self.get_window_bounds()
        titlebar_offset = 32
        device_h = wh - titlebar_offset
        cx = wx + int(ww * 0.5)
        cy = wy + titlebar_offset + int(device_h * 0.5)

        dx, dy = 0, 0
        if direction.upper() == "UP":
            dy = -200
        elif direction.upper() == "DOWN":
            dy = 200
        elif direction.upper() == "LEFT":
            dx = -150
        elif direction.upper() == "RIGHT":
            dx = 150

        # Fast drag using System Events
        script = f"""
        tell application "Simulator" to activate
        tell application "System Events"
            set startPt to {{{cx}, {cy}}}
            set endPt to {{{cx + dx}, {cy + dy}}}
            -- Perform drag
            click at startPt
        end tell
        """
        subprocess.run(["osascript", "-e", script], capture_output=True)
        time.sleep(0.8)

    def press_back(self) -> None:
        # Tap top-left back/cancel area (norm_x=80, norm_y=60)
        self.tap(80, 60)
