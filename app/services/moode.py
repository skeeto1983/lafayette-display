import json
import sqlite3
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from mpd import MPDClient
from mpd.base import ConnectionError as MPDConnectionError


class MoodeClient:
    """Read normalized playback information from moOde."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6600,
        timeout: int = 10,
        spotify_metadata_file: str = "/var/local/www/spotmeta.json",
        moode_database: str = "/var/local/www/db/moode-sqlite3.db",
        moode_web_url: str = "http://localhost",
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.spotify_metadata_file = Path(spotify_metadata_file)
        self.moode_database = Path(moode_database)
        self.moode_web_url = moode_web_url.rstrip("/")

    def get_current_playback(self) -> dict[str, Any]:
        """Return playback information from the active source."""

        if self._spotify_is_active():
            spotify = self._get_spotify_playback()

            if spotify is not None:
                return spotify

        return self._get_mpd_playback()

    def _spotify_is_active(self) -> bool:
        try:
            with sqlite3.connect(self.moode_database) as connection:
                row = connection.execute(
                    """
                    SELECT value
                    FROM cfg_system
                    WHERE param = 'spotactive'
                    """
                ).fetchone()

            return row is not None and row[0] == "1"

        except (OSError, sqlite3.Error):
            return False

    def _get_spotify_playback(self) -> dict[str, Any] | None:
        try:
            with self.spotify_metadata_file.open(
                "r",
                encoding="utf-8",
            ) as metadata_file:
                metadata = json.load(metadata_file)

        except (OSError, json.JSONDecodeError):
            return None

        duration_ms = self._to_float(metadata.get("duration"))

        return {
            "source": "Spotify Connect",
            "station": None,
            "state": "play",
            "artist": metadata.get("artist"),
            "album": metadata.get("album"),
            "title": metadata.get("title"),
            "elapsed": None,
            "duration": (
                duration_ms / 1000
                if duration_ms is not None
                else None
            ),
            "volume": None,
            "bitrate": self._extract_bitrate(
                metadata.get("sformat")
            ),
            "audio": metadata.get("sformat"),
            "file": None,
            "artwork": (
                metadata.get("cover_url")
                or "/static/images/placeholder.svg"
            ),
            "is_live": False,
        }

    def _get_mpd_playback(self) -> dict[str, Any]:
        client = self._connect()

        try:
            status = client.status()
            song = client.currentsong()

            raw_title = song.get("title")
            raw_station = song.get("name")

            title = raw_title
            artist = song.get("artist")

            if not artist and title and " - " in title:
                artist, title = title.split(" - ", 1)

            file_path = song.get("file")

            is_live = bool(
                file_path
                and file_path.startswith(
                    ("http://", "https://")
                )
            )

            artwork = "/static/images/placeholder.svg"

            if is_live:
                radio_artwork = self._get_radio_artwork(
                    title=raw_title,
                    station=raw_station,
                )

                if radio_artwork:
                    artwork = radio_artwork

            bitrate = self._to_int(status.get("bitrate"))

            if bitrate == 0:
                bitrate = None

            return {
                "source": (
                    "Internet Radio"
                    if is_live
                    else "moOde Audio"
                ),
                "station": self._clean_station_name(
                    raw_station
                ),
                "state": status.get("state", "stop"),
                "artist": artist,
                "album": song.get("album"),
                "title": title,
                "elapsed": self._to_float(
                    status.get("elapsed")
                ),
                "duration": self._to_float(
                    song.get("duration")
                    or status.get("duration")
                ),
                "volume": self._to_int(
                    status.get("volume")
                ),
                "bitrate": bitrate,
                "audio": status.get("audio"),
                "file": file_path,
                "artwork": artwork,
                "is_live": is_live,
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

    def _get_radio_artwork(
        self,
        title: str | None,
        station: str | None,
    ) -> str | None:
        if not title or not station:
            return None

        query = urlencode(
            {
                "cmd": "get_radiocover_url",
                "title": title,
                "station": station,
            }
        )

        url = (
            f"{self.moode_web_url}"
            f"/command/radio.php?{query}"
        )

        try:
            with urlopen(url, timeout=3) as response:
                payload = response.read().decode("utf-8")

            artwork = json.loads(payload)

            if (
                isinstance(artwork, str)
                and artwork.startswith(
                    ("http://", "https://")
                )
            ):
                return artwork

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
        ):
            return None

        return None

    def _connect(self) -> MPDClient:
        client = MPDClient()
        client.timeout = self.timeout
        client.idletimeout = None
        client.connect(self.host, self.port)
        return client

    @staticmethod
    def _clean_station_name(
        value: str | None,
    ) -> str | None:
        if not value:
            return None

        cleaned = value.replace("(flac)", "").strip()
        return cleaned or None

    @staticmethod
    def _extract_bitrate(
        value: str | None,
    ) -> int | None:
        if not value:
            return None

        digits = "".join(
            character
            for character in value
            if character.isdigit()
        )

        try:
            return int(digits) if digits else None
        except ValueError:
            return None

    @staticmethod
    def _to_int(value: Any) -> int | None:
        try:
            return (
                int(value)
                if value is not None
                else None
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            return (
                float(value)
                if value is not None
                else None
            )
        except (TypeError, ValueError):
            return None
