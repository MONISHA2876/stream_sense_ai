from fastapi import FastAPI
from app.video.metadata import get_video_metadata

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