const elements = {
    source: document.getElementById("source"),
    title: document.getElementById("title"),
    artist: document.getElementById("artist"),
    album: document.getElementById("album"),
    artwork: document.getElementById("artwork"),
    elapsed: document.getElementById("elapsed"),
    duration: document.getElementById("duration"),
    progressBar: document.getElementById("progress-bar"),
    clock: document.getElementById("clock"),
};

function formatTime(totalSeconds) {
    const secondsValue = Number(totalSeconds);

    if (!Number.isFinite(secondsValue) || secondsValue < 0) {
        return "0:00";
    }

    const minutes = Math.floor(secondsValue / 60);
    const seconds = Math.floor(secondsValue % 60);

    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function parseRadioMetadata(status) {
    let artist = status.artist || "";
    let title = status.title || "No title";

    /*
     * Many internet-radio stations provide metadata as:
     * "Artist - Track"
     *
     * Split it only when MPD did not already provide an artist.
     */
    if (!artist && title.includes(" - ")) {
        const separatorIndex = title.indexOf(" - ");

        artist = title.slice(0, separatorIndex).trim();
        title = title.slice(separatorIndex + 3).trim();
    }

    return { artist, title };
}

function getSourceLabel(status) {
    if (status.station) {
        return status.station;
    }

    if (status.file?.startsWith("http")) {
        return "Internet Radio";
    }

    return status.source || "moOde Audio";
}

function updateDisplay(status) {
    const metadata = parseRadioMetadata(status);

    elements.source.textContent = getSourceLabel(status);
    elements.title.textContent = metadata.title;
    elements.artist.textContent = metadata.artist;
    elements.album.textContent = status.album || "";

    const newArtwork =
        status.artwork || "/static/images/placeholder.svg";

    if (elements.artwork.src !== new URL(newArtwork, window.location.href).href) {
        elements.artwork.classList.add("artwork-fade-out");

        setTimeout(() => {
            elements.artwork.src = newArtwork;

            elements.artwork.onload = () => {
                elements.artwork.classList.remove("artwork-fade-out");
            };
        }, 200);
    }

    const elapsed = Number(status.elapsed) || 0;
    const duration = Number(status.duration) || 0;
    const hasDuration = duration > 0;

    elements.elapsed.textContent = hasDuration
        ? formatTime(elapsed)
        : "LIVE";

    elements.duration.textContent = hasDuration
        ? formatTime(duration)
        : "";

    const progress = hasDuration
        ? Math.min(100, Math.max(0, (elapsed / duration) * 100))
        : 0;

    elements.progressBar.style.width = `${progress}%`;
}

async function fetchStatus() {
    try {
        const response = await fetch("/api/status", {
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const status = await response.json();
        updateDisplay(status);
    } catch (error) {
        console.error("Unable to fetch playback status:", error);

        elements.source.textContent = "moOde unavailable";
        elements.title.textContent = "Connection lost";
        elements.artist.textContent = "";
        elements.album.textContent = "";
        elements.elapsed.textContent = "";
        elements.duration.textContent = "";
        elements.progressBar.style.width = "0%";
    }
}

function updateClock() {
    const now = new Date();

    elements.clock.textContent = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

fetchStatus();
updateClock();

setInterval(fetchStatus, 2000);
setInterval(updateClock, 1000);
