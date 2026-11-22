import subprocess
from pathlib import Path


class VideoSegmenter:
    def __init__(
        self,
        source: str,
        output_dir: str,
        segment_duration: int = 10,
        realtime: bool = False
    ):
        self.source = Path(source)
        self.output_dir = Path(output_dir)
        self.segment_duration = segment_duration
        self.realtime = realtime

        self.process: subprocess.Popen | None = None
        self.log_file = None

        self.manifest_path = self.output_dir / "segments.csv"

    def start(self):
        """Start splitting the input video into segments."""

        if self.process is not None and self.process.poll() is None:
            raise RuntimeError("Segmenter is already running.")

        if not self.source.is_file():
            raise FileNotFoundError(
                f"Source video not found: {self.source}"
            )

        if self.segment_duration <= 0:
            raise ValueError("Segment duration must be positive.")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = self.output_dir / "segment_%06d.mkv"

        log_path = self.output_dir / "segmenter.ffmpeg.log"
        self.log_file = open(log_path, "w", encoding="utf-8")

        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
        ]

        if self.realtime:
            command.append("-re")

        command.extend([
            "-i", str(self.source),
            "-map", "0:v:0",
            "-map", "0:a:0?",
            "-c", "copy",
            "-f", "segment",
            "-segment_time", str(self.segment_duration),
            "-reset_timestamps", "1",
            "-segment_list", str(self.manifest_path),
            "-segment_list_type", "csv",
            "-segment_list_size", "0",
            "-y",
            str(output_pattern)
        ])

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=self.log_file
            )
        except FileNotFoundError as exc:
            self._close_log()
            raise RuntimeError("FFmpeg was not found.") from exc

        return self.process.pid

    def is_running(self) -> bool:
        """ Check whether FFmpeg is running """

        return (
            self.process is not None
            and self.process.poll() is None
        )

    def wait(self, timeout: int | None = None):
        """ Wait for segmentation to finish """

        if self.process is None:
            raise RuntimeError("Segmenter has not been started.")

        try:
            return_code = self.process.wait(timeout=timeout)
        finally:
            if self.process.poll() is not None:
                self._close_log()

        if return_code != 0:
            raise RuntimeError(
                f"FFmpeg segmentation failed with exit code {return_code}."
            )

        return return_code

    def stop(self, timeout: int = 10):
        """Stop FFmpeg gracefully."""

        if self.process is None:
            return None

        try:
            if self.process.poll() is None:
                self.process.terminate()

                try:
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

            return self.process.returncode

        finally:
            self._close_log()

    def _close_log(self):
        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None
