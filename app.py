from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/status")
def status():
    """
    Temporary playback information.

    This will later be replaced with live information from moOde.
    """
    return jsonify(
        {
            "source": "Lafayette Streamer",
            "state": "idle",
            "artist": "No artist",
            "title": "Ready",
            "album": "",
            "elapsed": 0,
            "duration": 0,
            "artwork": "/static/images/placeholder.svg",
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
