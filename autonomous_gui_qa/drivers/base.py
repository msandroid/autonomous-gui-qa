"""
Base Device Driver Abstract Interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseDeviceDriver(ABC):
    """Abstract device interaction driver for mobile OS."""

    @abstractmethod
    def tap(self, x: int, y: int) -> None:
        """Tap at normalized coordinate (0-1000)."""
        pass

    @abstractmethod
    def type_text(self, text: str) -> None:
        """Type text into current focus."""
        pass

    @abstractmethod
    def swipe(self, direction: str) -> None:
        """Swipe UP | DOWN | LEFT | RIGHT."""
        pass

    @abstractmethod
    def press_back(self) -> None:
        """Press back button or dismiss sheet."""
        pass

    @abstractmethod
    def take_screenshot(self, output_filename: str) -> str:
        """Captures device screen and returns absolute file path."""
        pass

    @abstractmethod
    def set_appearance(self, mode: str) -> None:
        """Set appearance mode: light | dark."""
        pass
