import math
import struct
import subprocess
import threading
from typing import Any


class VUService:
    """Continuously read stereo PCM and expose the latest RMS levels."""

    def __init__(
        self,
        device: str = "hw:Loopback,1",
        sample_rate: int = 44100,
        channels: int = 2,
        sample_format: str = "S16_LE",
        chunk_frames: int = 2048,
    ) -> None:
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_format = sample_format
        self.chunk_frames = chunk_frames

        self._left_db = -60.0
        self._right_db = -60.0

        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._process: subprocess.Popen[bytes] | None = None
        self._running = False

    def start(self) -> None:
        """Start the background audio reader."""

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            name="lafayette-vu",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the background audio reader."""

        self._running = False

        if self._process is not None:
            self._process.terminate()

        if self._thread is not None:
            self._thread.join(timeout=2)

    def get_levels(self) -> dict[str, float]:
        """Return the most recently calculated stereo levels."""

        with self._lock:
            return {
                "left_db": round(self._left_db, 1),
                "right_db": round(self._right_db, 1),
            }

    def _run(self) -> None:
        command = [
            "arecord",
            "-D",
            self.device,
            "-f",
            self.sample_format,
            "-c",
            str(self.channels),
            "-r",
            str(self.sample_rate),
            "-t",
            "raw",
        ]

        bytes_per_frame = self.channels * 2
        chunk_size = self.chunk_frames * bytes_per_frame

        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )

            if self._process.stdout is None:
                return

            while self._running:
                raw = self._process.stdout.read(chunk_size)

                if not raw or len(raw) < chunk_size:
                    break

                samples = struct.unpack(
                    "<" + "h" * (len(raw) // 2),
                    raw,
                )

                left = samples[0::2]
                right = samples[1::2]

                left_db = self._dbfs(left)
                right_db = self._dbfs(right)

                with self._lock:
                    self._left_db = left_db
                    self._right_db = right_db

        finally:
            if self._process is not None:
                self._process.terminate()

                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()

            self._process = None
            self._running = False

    @staticmethod
    def _dbfs(samples: tuple[int, ...]) -> float:
        if not samples:
            return -60.0

        mean_square = sum(
            sample * sample
            for sample in samples
        ) / len(samples)

        if mean_square <= 0:
            return -60.0

        rms = math.sqrt(mean_square)
        db = 20 * math.log10(rms / 32768)

        return max(-60.0, db)
