import argparse
import json
import sys

from charging_network import is_station_available
from sentinel_client import SentinelClient, SentinelAPIError


def build_parser():
    parser = argparse.ArgumentParser(
        description="ChargePoint Sentinel EV charging checker"
    )

    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:5000"
    )

    parser.add_argument(
        "--session-header",
        default=None,
        help="Optional X-Session-Id header"
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True
    )

    sub.add_parser("health")
    sub.add_parser("stations")

    station = sub.add_parser("station")
    station.add_argument("station_id")

    start = sub.add_parser("start")
    start.add_argument("station_id")
    start.add_argument("vehicle_id")

    update = sub.add_parser("update-session")
    update.add_argument("session_id")
    update.add_argument(
        "status",
        choices=["active", "completed", "cancelled"]
    )

    delete = sub.add_parser("delete-session")
    delete.add_argument("session_id")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    headers = {}
    if args.session_header:
        headers["X-Session-Id"] = args.session_header

    client = SentinelClient(
        base_url=args.base_url,
        headers=headers
    )

    try:
        if args.command == "health":
            result = client.health()

        elif args.command == "stations":
            result = client.list_stations()

            for station in result:
                station["available"] = is_station_available(
                    station
                )

        elif args.command == "station":
            result = client.get_station(args.station_id)
            result["available"] = is_station_available(result)

        elif args.command == "start":
            result = client.create_session(
                args.station_id,
                args.vehicle_id
            )

        elif args.command == "update-session":
            result = client.update_session(
                args.session_id,
                args.status
            )

        elif args.command == "delete-session":
            client.delete_session(args.session_id)
            result = {
                "deleted": True,
                "session_id": args.session_id
            }

        print(json.dumps(result, indent=2))
        return 0

    except SentinelAPIError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())