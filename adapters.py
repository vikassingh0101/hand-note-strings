"""Turn raw MediaPipe-plugin channel values into a HandFrame.

Channel names follow the MediaPipe TouchDesigner plugin: "h1:thumb_tip:x",
"h1:index_finger_tip:y", "h1:wrist:x", "h1:hand_active", ...
"""
from __future__ import annotations

import math
from typing import Mapping, Optional

from .engine import HandFrame


def _dist(ax: float, ay: float, bx: float, by: float, aspect: float) -> float:
    # y is scaled by aspect (frame height / width) so distances are isotropic.
    return math.hypot(ax - bx, (ay - by) * aspect)


def frame_from_channels(
    values: Mapping[str, float],
    *,
    hand: str = "h1",
    aspect: float = 9.0 / 16.0,
    flip_y: bool = True,
    mirror_x: bool = False,
    default_hand_size: float = 0.12,
    t: float = 0.0,
) -> HandFrame:
    """Build a HandFrame from a {channel_name: value} mapping.

    flip_y:   MediaPipe's y grows downward; True makes y grow upward.
    mirror_x: flip left/right if your camera image is mirrored the wrong way.
    The pinch ratio is thumb-tip/index-tip distance divided by hand size
    (wrist -> middle_finger_mcp), so it doesn't depend on how far you are from
    the camera. If the hand-size channels are missing, default_hand_size is used.
    """

    def get(landmark: str, axis: str) -> Optional[float]:
        return values.get("%s:%s:%s" % (hand, landmark, axis))

    tx, ty = get("thumb_tip", "x"), get("thumb_tip", "y")
    ix, iy = get("index_finger_tip", "x"), get("index_finger_tip", "y")
    if tx is None or ty is None or ix is None or iy is None:
        return HandFrame(present=False, t=t)

    active = values.get("%s:hand_active" % hand)
    if active is not None and active < 0.5:
        return HandFrame(present=False, t=t)

    size = default_hand_size
    wx, wy = get("wrist", "x"), get("wrist", "y")
    mx, my = get("middle_finger_mcp", "x"), get("middle_finger_mcp", "y")
    if wx is not None and wy is not None and mx is not None and my is not None:
        measured = _dist(wx, wy, mx, my, aspect)
        if measured > 1e-6:
            size = measured

    x = (tx + ix) / 2.0
    y = (ty + iy) / 2.0
    if mirror_x:
        x = 1.0 - x
    if flip_y:
        y = 1.0 - y

    return HandFrame(
        present=True,
        x=x,
        y=y,
        pinch_ratio=_dist(tx, ty, ix, iy, aspect) / size,
        t=t,
    )
