from fastapi import FastAPI

app = FastAPI(title="StreamSense AI")

@app.get("/")
def Home():
    return {"message":"StreamSense AI server running!"}