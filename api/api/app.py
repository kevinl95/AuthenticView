import io, os
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()


@app.post("/analyze")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, "wb") as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the image"}
    finally:
        file.file.close()
    return FileResponse(
        file_path, media_type="image/jpeg", filename="vector_image_for_you.jpg"
    )
