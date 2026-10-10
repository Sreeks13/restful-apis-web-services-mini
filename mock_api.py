from copy import deepcopy
from flask import Flask, jsonify, request

DEFAULT_STATIONS = [
    {
        "station_id": "ST-100",
        "name": "Central Mall",
        "location": "Bengaluru",
        "available_ports": 3,
        "total_ports": 4,
        "status": "online"
    },
    {
        "station_id": "ST-200",
        "name": "Tech Park",
        "location": "Hyderabad",
        "available_ports": 0,
        "total_ports": 6,
        "status": "online"
    },
    {
        "station_id": "ST-300",
        "name": "Highway Hub",
        "location": "Chennai",
        "available_ports": 2,
        "total_ports": 4,
        "status": "offline"
    }
]


def create_app(initial_stations=None):
    app = Flask(__name__)
    app.config["stations"] = deepcopy(
        initial_stations if initial_stations is not None
        else DEFAULT_STATIONS
    )
    app.config["sessions"] = {}
    app.config["next_session_id"] = 1

    def find_station(station_id):
        return next(
            (
                station for station in app.config["stations"]
                if station["station_id"] == station_id
            ),
            None
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.get("/stations")
    def list_stations():
        return jsonify({
            "stations": app.config["stations"]
        }), 200

    @app.get("/stations/<station_id>")
    def get_station(station_id):
        station = find_station(station_id)

        if station is None:
            return jsonify({"error": "station not found"}), 404

        return jsonify(station), 200

    @app.post("/sessions")
    def create_session():
        payload = request.get_json(silent=True) or {}

        station_id = str(payload.get("station_id", "")).strip()
        vehicle_id = str(payload.get("vehicle_id", "")).strip()

        if not station_id or not vehicle_id:
            return jsonify({
                "error": "station_id and vehicle_id are required"
            }), 400

        station = find_station(station_id)

        if station is None:
            return jsonify({"error": "station not found"}), 404

        if (
            station["status"] != "online"
            or station["available_ports"] < 1
        ):
            return jsonify({
                "error": "station is unavailable"
            }), 409

        session_id = (
            f"CS-{app.config['next_session_id']:04d}"
        )
        app.config["next_session_id"] += 1

        session = {
            "session_id": session_id,
            "station_id": station_id,
            "vehicle_id": vehicle_id,
            "status": "active"
        }

        app.config["sessions"][session_id] = session
        station["available_ports"] -= 1

        return jsonify(session), 201

    @app.get("/sessions/<session_id>")
    def get_session(session_id):
        session = app.config["sessions"].get(session_id)

        if session is None:
            return jsonify({"error": "session not found"}), 404

        return jsonify(session), 200

    @app.patch("/sessions/<session_id>")
    def update_session(session_id):
        session = app.config["sessions"].get(session_id)

        if session is None:
            return jsonify({"error": "session not found"}), 404

        payload = request.get_json(silent=True) or {}

        if "status" in payload:
            if payload["status"] not in (
                "active", "completed", "cancelled"
            ):
                return jsonify({
                    "error": "invalid session status"
                }), 400

            session["status"] = payload["status"]

        return jsonify(session), 200

    @app.put("/stations/<station_id>")
    def replace_station(station_id):
        station = find_station(station_id)

        if station is None:
            return jsonify({"error": "station not found"}), 404

        payload = request.get_json(silent=True) or {}

        required = (
            "name", "location", "available_ports",
            "total_ports", "status"
        )

        if any(key not in payload for key in required):
            return jsonify({
                "error": "all station fields are required"
            }), 400

        try:
            available = int(payload["available_ports"])
            total = int(payload["total_ports"])
        except (TypeError, ValueError):
            return jsonify({"error": "invalid port count"}), 400

        if total < 1 or available < 0 or available > total:
            return jsonify({"error": "invalid port count"}), 400

        if payload["status"] not in ("online", "offline"):
            return jsonify({"error": "invalid station status"}), 400

        station.update({
            "name": payload["name"],
            "location": payload["location"],
            "available_ports": available,
            "total_ports": total,
            "status": payload["status"]
        })

        return jsonify(station), 200

    @app.delete("/sessions/<session_id>")
    def delete_session(session_id):
        session = app.config["sessions"].pop(session_id, None)

        if session is None:
            return "", 404

        station = find_station(session["station_id"])

        if station and session["status"] == "active":
            station["available_ports"] = min(
                station["total_ports"],
                station["available_ports"] + 1
            )

        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )