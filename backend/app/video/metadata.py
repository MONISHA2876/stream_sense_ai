import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from fractions import Fraction

@dataclass
class VideoMetadata:
    filename:str
    duration:float
    size:int
    width:int
    height:int
    video_codec:str
    frame_rate:float
    audio_codec:str|None

def parse_frame_rate(value:str|None)->float:
    """ Convert the frame rate from 300000/1001 format into float """

    #handle the missing value
    if not value or value=="0/0":
        return 0.0
    try:
        return float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return 0.0

def get_video_metadata(video_path:str)->VideoMetadata:
    """ To get the meta data of the video path given """

    path = Path(video_path)

    #if the do not exist
    if not path.is_file():
        raise FileNotFoundError(f"File not found on path {path}")

    #ffprobe command
    command = [
        "ffprobe","-v","quiet","-show_format","-show_streams","-of","json",path
    ]

    #get result from ffprobe
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"ffprobe not found try installing FFmpeg"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"ffprobe failed : {exc.stderr.strip()}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "ffprobe timed out."
        ) from exc


    # parse the json response
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid response from ffprobe") from exc

    streams = data.get("streams", [])
    format_info = data.get("format", {})\
    

    # find video and audio streams
    video_stream = next(
        (s for s in streams if s.get("codec_type") == "video"),
        None
    )

    audio_stream = next(
        (s for s in streams if s.get("codec_type") == "audio"),
        None
    )

    if video_stream is None:
        raise ValueError("No video stream found in the file")


    frame_rate_value = (
        video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")
    )

    frame_rate = parse_frame_rate(value = str(frame_rate_value))

    return VideoMetadata(
        filename=path.name,
        duration=float(format_info.get("duration", 0)),
        size=int(format_info.get("size")),
        width=int(video_stream.get("width")),
        height=int(video_stream.get("height")),
        video_codec=video_stream.get("codec_name", "unknown"),
        frame_rate=frame_rate,
        audio_codec=(
            audio_stream.get("codec_name") if audio_stream else None
        )
    )