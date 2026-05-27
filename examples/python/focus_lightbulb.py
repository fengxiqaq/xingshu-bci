"""专注力意念控灯泡示例 — Focus-controlled lightbulb.

Streams real-time concentration prediction from the local XingShu BCI
API and maps it to a smart bulb's on/off + brightness. All the noisy
parts (EMA smoothing, hysteresis, rate limiting, dead-zone mapping)
are handled by ``SmoothedFocusStream`` from the SDK — application code
just reads each ``FocusUpdate`` and drives the bulb.

Real-world bulb drivers
-----------------------
Replace ``StubBulb`` with one of:

* **Yeelight**       — ``pip install yeelight`` → ``yeelight.Bulb(ip)``
* **TP-Link Kasa**   — ``pip install python-kasa`` → ``SmartBulb(ip)``
* **Philips Hue**    — ``pip install phue`` → ``Bridge(...)``
* **Home Assistant** — ``POST /api/services/light/turn_on`` over HTTP
* **Tuya / Smart Life** — ``pip install tinytuya``
* **MQTT / Tasmota** — publish ``cmnd/<dev>/Power`` + ``cmnd/<dev>/Dimmer``

Every driver only needs three methods: ``on()`` / ``off()`` /
``set_brightness(percent)``.
"""

from __future__ import annotations

from typing import Protocol

from xingshu_bci import SmoothedFocusStream, XingShuClient


class LightBulb(Protocol):
    def on(self) -> None: ...
    def off(self) -> None: ...
    def set_brightness(self, percent: int) -> None: ...


class StubBulb:
    """Console-printing stub. Swap for a real driver in production."""

    def __init__(self) -> None:
        self._on = False
        self._b = 0

    def on(self) -> None:
        if not self._on:
            self._on = True
            print("[bulb] ON")

    def off(self) -> None:
        if self._on:
            self._on = False
            print("[bulb] OFF")

    def set_brightness(self, percent: int) -> None:
        percent = max(0, min(100, int(percent)))
        if percent != self._b:
            self._b = percent
            print(f"[bulb] {percent}%")


def main() -> None:
    bulb: LightBulb = StubBulb()

    with XingShuClient.auto() as client:
        if client.status().state == "idle":
            client.connect(board="synthetic", transport="synthetic")

        print("[ready] focus your mind to brighten the bulb (Ctrl+C to stop)")
        stream = SmoothedFocusStream(client, metric="concentration")
        for upd in stream:
            if upd.rising:
                bulb.on()
            elif upd.falling:
                bulb.off()
            if upd.is_on:
                bulb.set_brightness(upd.brightness)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bye]")
