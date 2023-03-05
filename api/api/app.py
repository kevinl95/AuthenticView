import asyncio, io, os, subprocess, uuid, shutil
import uvicorn
from fastapi import FastAPI, File, UploadFile
from starlette.responses import StreamingResponse
from io import BytesIO

app = FastAPI()


@app.post("/analyze")
def upload(file: UploadFile = File(...)):
    origDir = os.getcwd()
    os.chdir("FALdetector")
    session = str(uuid.uuid4())
    contents = file.file.read()
    filePath = file.filename
    with open(filePath, "wb") as f:
        f.write(contents)
    scriptPath = "local_detector.py"
    weightsPath = os.path.join("weights", "local.pth")
    if not os.path.exists(session):
        os.makedirs(session)
    analyze_cmd = (
        "poetry run python "
        + scriptPath
        + " --input_path "
        + filePath
        + " --model_path "
        + weightsPath
        + " --dest_folder "
        + session
    )
    p = subprocess.Popen(analyze_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    try:
        pass
    except Exception:
        return {"message": "There was an error handling the image"}
    finally:
        file.file.close()
    image = None
    with open(os.path.join(session, "warped.jpg"), "rb") as fh:
        image = fh.read()
    # Cleanup
    os.remove(filePath)
    shutil.rmtree(session)
    os.chmod(origDir)
    return StreamingResponse(image, media_type="image/jpeg")
