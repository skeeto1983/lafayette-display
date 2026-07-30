from typing import Any

from mpd import MPDClient
from mpd.base import ConnectionError as MPDConnectionError


class MoodeClient:
    """Wrapper around moOde's MPD server."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6600,
        timeout: int = 10,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def _connect(self) -> MPDClient:
        client = MPDClient()
        client.timeout = self.timeout
        client.idletimeout = None
        client.connect(self.host, self.port)
        return client

    def get_current_playback(self) -> dict[str, Any]:
        client = self._connect()

        try:
            status = client.status()
            song = client.currentsong()

            return {
                "state": status.get("state", "stop"),
                "volume": self._to_int(status.get("volume")),
                "elapsed": self._to_float(status.get("elapsed")),
                "duration": self._to_float(
                    song.get("duration") or status.get("duration")
                ),
                "bitrate": self._to_int(status.get("bitrate")),
                "audio": status.get("audio"),
                "artist": song.get("artist"),
                "album": song.get("album"),
                "title": song.get("title"),
                "station": song.get("name"),
                "file": song.get("file"),
            }
        finally:
            try:
                client.close()
            except MPDConnectionError:
                pass

            try:
                client.disconnect()
            except MPDConnectionError:
                pass

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
