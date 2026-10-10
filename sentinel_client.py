import requests


class SentinelAPIError(RuntimeError):
    pass


class SentinelClient:
    def __init__(
        self,
        base_url="http://127.0.0.1:5000",
        session=None,
        timeout=5,
        headers=None
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

        self.session.headers.update({
            "Accept": "application/json",
            **(headers or {})
        })

    def _request(self, method, path, **kwargs):
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                timeout=self.timeout,
                **kwargs
            )
        except requests.Timeout as exc:
            raise SentinelAPIError(
                f"Request timed out: {exc}"
            ) from exc
        except requests.ConnectionError as exc:
            raise SentinelAPIError(
                f"Could not connect to API: {exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                detail = response.json().get(
                    "error", response.text
                )
            except (ValueError, AttributeError):
                detail = response.text

            raise SentinelAPIError(
                f"HTTP {response.status_code}: {detail}"
            )

        return response

    @staticmethod
    def _json(response):
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def health(self):
        return self._json(self._request("GET", "/health"))

    def list_stations(self):
        result = self._json(
            self._request("GET", "/stations")
        )
        return result["stations"]

    def get_station(self, station_id):
        return self._json(
            self._request("GET", f"/stations/{station_id}")
        )

    def create_session(self, station_id, vehicle_id):
        return self._json(
            self._request(
                "POST",
                "/sessions",
                json={
                    "station_id": station_id,
                    "vehicle_id": vehicle_id
                }
            )
        )

    def update_session(self, session_id, status):
        return self._json(
            self._request(
                "PATCH",
                f"/sessions/{session_id}",
                json={"status": status}
            )
        )

    def replace_station(self, station_id, station):
        return self._json(
            self._request(
                "PUT",
                f"/stations/{station_id}",
                json=station
            )
        )

    def delete_session(self, session_id):
        self._request("DELETE", f"/sessions/{session_id}")