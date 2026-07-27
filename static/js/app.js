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

function updateDisplay(status) {
    elements.source.textContent = status.source || "Unknown source";
    elements.title.textContent = status.title || "No title";
    elements.artist.textContent = status.artist || "";
    elements.album.textContent = status.album || "";

    if (status.artwork) {
        elements.artwork.src = status.artwork;
    }

    const elapsed = Number(status.elapsed) || 0;
    const duration = Number(status.duration) || 0;

    elements.elapsed.textContent = formatTime(elapsed);
    elements.duration.textContent = formatTime(duration);

    const progress =
        duration > 0
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
        elements.source.textContent = "Connection unavailable";
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
