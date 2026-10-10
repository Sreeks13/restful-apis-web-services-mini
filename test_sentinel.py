import unittest
from unittest.mock import Mock

import requests

from charging_network import is_station_available
from sentinel_client import SentinelClient, SentinelAPIError


class ChargingNetworkTests(unittest.TestCase):
    def test_available_station(self):
        self.assertTrue(
            is_station_available({
                "status": "online",
                "available_ports": 1
            })
        )

        self.assertFalse(
            is_station_available({
                "status": "offline",
                "available_ports": 1
            })
        )

        self.assertFalse(
            is_station_available({
                "status": "online",
                "available_ports": 0
            })
        )


class SentinelClientTests(unittest.TestCase):
    def test_get_station_uses_session_header(self):
        session = Mock(spec=requests.Session)
        session.headers = {}

        response = Mock()
        response.status_code = 200
        response.content = b'{"station_id":"ST-100"}'
        response.json.return_value = {
            "station_id": "ST-100"
        }

        session.request.return_value = response

        client = SentinelClient(
            session=session,
            headers={"X-Session-Id": "abc-123"}
        )

        result = client.get_station("ST-100")

        self.assertEqual(result["station_id"], "ST-100")
        self.assertEqual(
            session.headers["X-Session-Id"],
            "abc-123"
        )

    def test_http_error_raises(self):
        session = Mock(spec=requests.Session)
        session.headers = {}

        response = Mock()
        response.status_code = 404
        response.text = '{"error":"station not found"}'
        response.json.return_value = {
            "error": "station not found"
        }

        session.request.return_value = response

        client = SentinelClient(session=session)

        with self.assertRaises(SentinelAPIError):
            client.get_station("missing")


if __name__ == "__main__":
    unittest.main()