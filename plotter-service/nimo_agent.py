#!/usr/bin/env python3
import argparse
import time
import requests
import sys


def poll_next_job(api_base: str, plotter_id: str, interval_s: int = 15):
    while True:
        try:
            r = requests.get(f"{api_base}/jobs/next", params={"plotter_id": plotter_id}, timeout=30)
            if r.status_code == 204:
                time.sleep(interval_s)
                continue
            r.raise_for_status()
            job = r.json()
            job_id = job["id"]
            svg_text = job["svg_text"]

            # mark started
            requests.post(f"{api_base}/jobs/{job_id}/status", json={"status": "started", "notes": "processing"}, timeout=30)

            # TODO: write svg_text to file, convert to gcode, stream to GRBL via serial
            # Placeholder work
            time.sleep(2)

            # mark completed
            requests.post(f"{api_base}/jobs/{job_id}/status", json={"status": "completed", "notes": "done"}, timeout=30)
        except Exception as e:
            print(f"Agent error: {e}", file=sys.stderr)
            time.sleep(interval_s)


def main():
    p = argparse.ArgumentParser(description="Nimo plotter agent")
    p.add_argument("--api", required=True, help="API base URL, e.g. https://nimo.fly.dev")
    p.add_argument("--plotter-id", default="NIMO-01", help="Plotter identifier")
    p.add_argument("--interval", type=int, default=15, help="Polling interval seconds")
    p.add_argument("--port", help="Serial port to GRBL (e.g., /dev/ttyUSB0)")
    args = p.parse_args()

    print(f"Starting agent for {args.plotter_id} against {args.api}")
    poll_next_job(args.api.rstrip("/"), args.plotter_id, args.interval)


if __name__ == "__main__":
    main()


