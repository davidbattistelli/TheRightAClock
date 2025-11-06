#!/usr/bin/env python3
"""
Simple command-line bedtime calculator

This script calls the SleepCycle-Alarm API to calculate optimal bedtimes.

Usage:
    python bedtime_calculator.py 07:30
    python bedtime_calculator.py 06:00 --latency 20 --cycle 85

Requirements:
    pip install requests
"""
import sys
import argparse
import requests
from typing import Optional


API_URL = "http://localhost:8000/api/v1/calculate"


def calculate_bedtimes(
    wake_time: str,
    sleep_latency_min: int = 15,
    cycle_length_min: int = 90,
    min_cycles: int = 4,
    max_cycles: int = 6
):
    """
    Calculate bedtimes for given wake time

    Args:
        wake_time: Wake time in HH:MM format
        sleep_latency_min: Minutes to fall asleep
        cycle_length_min: Sleep cycle duration
        min_cycles: Minimum cycles to show
        max_cycles: Maximum cycles to show
    """
    try:
        response = requests.post(
            API_URL,
            json={
                "wake_time": wake_time,
                "sleep_latency_min": sleep_latency_min,
                "cycle_length_min": cycle_length_min,
                "min_cycles": min_cycles,
                "max_cycles": max_cycles
            },
            timeout=5
        )

        if response.status_code != 200:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
            return

        data = response.json()
        display_results(data)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("   Try: docker-compose up")
        print("   Or: cd backend && uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def display_results(data: dict):
    """Display calculation results in a nice format"""
    wake_time = data["wake_time"]
    options = data["options"]
    params = data["parameters"]

    print("\n" + "="*60)
    print(f"🛏️  BEDTIME OPTIONS FOR WAKING AT {wake_time}")
    print("="*60)

    print(f"\nParameters:")
    print(f"  • Sleep latency: {params['sleep_latency_min']} minutes")
    print(f"  • Cycle length: {params['cycle_length_min']} minutes")
    print()

    for i, option in enumerate(options, 1):
        hours = int(option['total_sleep_hours'])
        minutes = int((option['total_sleep_hours'] - hours) * 60)

        recommended = "✅ RECOMMENDED" if option["recommended"] else ""

        print(f"{i}. Go to bed at: {option['bedtime']}")
        print(f"   • {option['cycles']} sleep cycles")
        print(f"   • Total sleep: {hours}h {minutes}m")
        print(f"   {recommended}")
        print()

    print("💤 Choose one of these times to wake up refreshed!")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate optimal bedtimes based on sleep cycles",
        epilog="Example: python bedtime_calculator.py 07:30 --latency 20"
    )

    parser.add_argument(
        "wake_time",
        help="Wake time in HH:MM format (24-hour)",
        type=str
    )

    parser.add_argument(
        "--latency",
        help="Minutes to fall asleep (default: 15)",
        type=int,
        default=15
    )

    parser.add_argument(
        "--cycle",
        help="Sleep cycle length in minutes (default: 90)",
        type=int,
        default=90
    )

    parser.add_argument(
        "--min-cycles",
        help="Minimum cycles to show (default: 4)",
        type=int,
        default=4,
        dest="min_cycles"
    )

    parser.add_argument(
        "--max-cycles",
        help="Maximum cycles to show (default: 6)",
        type=int,
        default=6,
        dest="max_cycles"
    )

    args = parser.parse_args()

    # Validate wake time format
    if ":" not in args.wake_time or len(args.wake_time.split(":")) != 2:
        print("❌ Error: Wake time must be in HH:MM format (e.g., 07:30)")
        sys.exit(1)

    calculate_bedtimes(
        wake_time=args.wake_time,
        sleep_latency_min=args.latency,
        cycle_length_min=args.cycle,
        min_cycles=args.min_cycles,
        max_cycles=args.max_cycles
    )


if __name__ == "__main__":
    main()
