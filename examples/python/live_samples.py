"""Subscribe to live samples + analysis via the XingShu BCI Python SDK."""

from __future__ import annotations

from xingshu_bci import XingShuClient


def main() -> None:
    with XingShuClient.auto() as client:
        print("API version:", client.version().apiVersion)
        print("Status:", client.status().state)

        # Optional: connect a synthetic board so samples flow immediately.
        if client.status().state == "idle":
            client.connect(board="synthetic", transport="synthetic")

        print("Subscribing to events (Ctrl+C to stop)...")
        try:
            for event in client.events(types=["samples", "analysis", "status"]):
                if event.type == "samples":
                    data = event.payload.get("data") or []
                    if data and data[0]:
                        print(f"samples: ch0[0]={data[0][0]:.3f}")
                elif event.type == "analysis":
                    focus = event.payload.get("focus")
                    if focus:
                        print(f"focus: {focus}")
                elif event.type == "status":
                    print(f"status: {event.payload.get('state')}")
        except KeyboardInterrupt:
            print("Stopped.")


if __name__ == "__main__":
    main()
