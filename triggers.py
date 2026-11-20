"""Gesture triggers."""
from __future__ import annotations

from typing import Optional


class PinchTrigger:
    """Schmitt trigger on a pinch ratio (thumb-index distance / hand size).

    Goes "down" when the ratio drops below `on_below`, and "up" when it rises
    above `off_above`. The gap between the two stops flicker around one threshold.
    Passing None (hand lost) releases a held pinch.
    """

    def __init__(self, on_below: float = 0.30, off_above: float = 0.50) -> None:
        if on_below >= off_above:
            raise ValueError("on_below must be smaller than off_above")
        self.on_below = on_below
        self.off_above = off_above
        self.down = False

    def update(self, ratio: Optional[float]) -> Optional[str]:
        """Returns "down", "up", or None when nothing changed."""
        if ratio is None:
            if self.down:
                self.down = False
                return "up"
            return None
        if not self.down and ratio < self.on_below:
            self.down = True
            return "down"
        if self.down and ratio > self.off_above:
            self.down = False
            return "up"
        return None

    def reset(self) -> None:
        self.down = False
