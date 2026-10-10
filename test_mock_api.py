import unittest
from mock_api import create_app


class MockAPITests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "healthy"
        )

    def test_list_stations(self):
        response = self.client.get("/stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.get_json()["stations"]),
            3
        )

    def test_unknown_station(self):
        response = self.client.get("/stations/missing")
        self.assertEqual(response.status_code, 404)

    def test_start_and_delete_session(self):
        response = self.client.post(
            "/sessions",
            json={
                "station_id": "ST-100",
                "vehicle_id": "EV-7"
            }
        )

        self.assertEqual(response.status_code, 201)
        session_id = response.get_json()["session_id"]

        response = self.client.get(
            f"/sessions/{session_id}"
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(
            f"/sessions/{session_id}"
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            f"/sessions/{session_id}"
        )
        self.assertEqual(response.status_code, 404)

    def test_unavailable_station(self):
        response = self.client.post(
            "/sessions",
            json={
                "station_id": "ST-200",
                "vehicle_id": "EV-7"
            }
        )
        self.assertEqual(response.status_code, 409)

    def test_patch_session(self):
        created = self.client.post(
            "/sessions",
            json={
                "station_id": "ST-100",
                "vehicle_id": "EV-9"
            }
        ).get_json()

        response = self.client.patch(
            f"/sessions/{created['session_id']}",
            json={"status": "completed"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "completed"
        )


if __name__ == "__main__":
    unittest.main()