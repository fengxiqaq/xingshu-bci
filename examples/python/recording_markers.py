"""Record a short synthetic session with event markers."""

from __future__ import annotations

import time

from xingshu_bci import XingShuClient


def main() -> None:
    with XingShuClient.auto() as client:
        client.connect(board="synthetic", transport="synthetic")
        try:
            client.start_recording()
            print("Recording started.")
            client.insert_marker(value=1, label="trial_start")
            time.sleep(2)
            client.insert_marker(value=2, label="stimulus_on")
            time.sleep(1)
            client.insert_marker(value=3, label="stimulus_off")
            time.sleep(2)
            client.insert_marker(value=4, label="trial_end")
            rec = client.stop_recording()
            print("Recording stopped:", rec)
            print("Final status:", client.recording_status())
        finally:
            client.disconnect()


if __name__ == "__main__":
    main()
