from fastapi import FastAPI
from app.video.metadata import get_video_metadata
from app.video.capture import VideoCapture
import time

app = FastAPI(title="StreamSense AI")

@app.get("/")
def Home():
    return {"message":"StreamSense AI server running!"}

@app.get("/video/")
def Metadata():
    try:
        return get_video_metadata("../storage/sample/sample.mp4")
    except FileNotFoundError:
        return {"message":"file not found check the path and try again"}

@app.get("/video/capture")
def Capture():
    capture = VideoCapture(
        source="../storage/sample/sample.mp4",
        output_path="../storage/buffer/capture.mkv",
        realtime=True
    )

    try:
        pid = capture.start()
        print("FFmpeg started PID : ", pid)

        for i in range(30):
            if not capture.is_running:
                print("FFmpeg finished before 10 sec")
                break
            print("Capturing ", i , "/30")
            time.sleep(1)

    finally:
        return_code = capture.stop()
        print("FFmpeg stopped. Exit Code : ", return_code)