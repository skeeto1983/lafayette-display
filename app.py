from flask import Flask, jsonify, send_from_directory

from app.services.moode import MoodeClient

app = Flask(__name__, static_folder="static")
moode = MoodeClient()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/status")
def status():
    try:
        playback = moode.get_current_playback()
        playback["artwork"] = "/static/images/placeholder.svg"
        return jsonify(playback)
    except Exception as exc:
        app.logger.exception("Unable to retrieve moOde playback status")

        return (
            jsonify(
                {
                    "state": "unavailable",
                    "artist": None,
                    "album": None,
                    "title": None,
                    "station": None,
                    "elapsed": None,
                    "duration": None,
                    "volume": None,
                    "bitrate": None,
                    "audio": None,
                    "file": None,
                    "artwork": "/static/images/placeholder.svg",
                    "error": str(exc),
                }
            ),
            503,
        )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
