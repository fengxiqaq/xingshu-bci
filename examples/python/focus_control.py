"""Poll the focus/relaxation analysis snapshot at 2 Hz."""

from __future__ import annotations

import time

from xingshu_bci import XingShuClient


def main() -> None:
    with XingShuClient.auto() as client:
        if client.status().state == "idle":
            client.connect(board="synthetic", transport="synthetic")
        print("Polling focus (Ctrl+C to stop)...")
        try:
            while True:
                snapshot = client.analysis_focus_latest()
                focus = snapshot.get("focus")
                if focus is None:
                    print("focus: --")
                else:
                    print(f"focus: {focus}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped.")


if __name__ == "__main__":
    main()
