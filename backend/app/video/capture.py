import subprocess
from pathlib import Path

class VideoCapture:
    def __init__(
            self,
            source:str,
            output_path:str,
            realtime:bool = False
    ):
        self.source = source
        self.output_path = Path(output_path)
        self.realtime = realtime

        self.process: subprocess.Popen|None = None
        self.log_file = None

    def start(self):
        """ Start capturing the video via using FFmpeg """

        # do not start if another process is already running
        if self.is_running():
            raise RuntimeError("Video capture is already running")

        self.source_path = Path(self.source)

        if not self.source_path.is_file():
            raise FileNotFoundError(f"Source video not found : {self.source}")

        self.output_path.parent.mkdir(
            parents = True,
            exist_ok = True
        )

        log_path = self.output_path.with_suffix(".ffmpeg.log")
        self.log_file = open(log_path, "w", encoding="utf-8")


        #ffmpeg command
        command = ["ffmpeg","-hide_banner","-loglevel","error"]

        # simulate the live stream here
        if self.realtime:
            command.append("-re")

        command.extend([
            "-i", str(self.source_path), "-map", "0:v:0", "-map", "0:a:0?", "-c","copy", "-y", str(self.output_path)
        ])

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=self.log_file
            )
        except FileNotFoundError as exc:
            self._close_log()
            raise RuntimeError(
                "FFmpeg is not found, try installing it"
            ) from exc

        return self.process.pid


    def is_running(self)->bool:
        """ Check whether the FFmpeg process is still running """
        return(
            self.process is not None and self.process.poll() is None
        )

    def stop(self, timeout:int = 10):
        """ Stops FFmpeg , force stop it if necessary """
        if self.process is None:
            return

        try:
            if self.process.poll() is None:
                self.process.terminate()

                try:
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

        finally:
            self._close_log()

        return self.process.returncode

    def _close_log(self):
        """ to close FFmpeg log file safely """

        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None