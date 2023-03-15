import asyncio, io, os, subprocess, uuid, shutil, base64
import uvicorn
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from starlette.responses import StreamingResponse
from io import BytesIO

description = """
Detecting manipulated photos with AI for body positivity. 🚀

## Analyze Photos

You can upload a photo to this API and receive a manipulation heatmap (as a JPEG) in response by using this endpint:

* **/analyze**

If there has been no manipulation detected you will get your original image back as a JPEG.
"""

app = FastAPI(
    title="AuthenticView API",
    description=description,
    version="1.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },

)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url='/docs')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

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
        "python3 "
        + scriptPath
        + " --input_path "
        + filePath
        + " --model_path "
        + weightsPath
        + " --dest_folder "
        + session
        + " --no_crop"
    )
    p = subprocess.Popen(analyze_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    file.file.close()
    image = None
    heatmap = os.path.join(session, "heatmap.jpg")
    if os.path.isfile(heatmap):
        with open(heatmap, "rb") as fh:
            image = fh.read()
    # Cleanup
    os.remove(filePath)
    shutil.rmtree(session)
    os.chdir(origDir)
    if image:
        return StreamingResponse(BytesIO(image), media_type="image/jpeg")
    else:
        return StreamingResponse(BytesIO(contents), media_type="image/jpeg")

@app.post("/analyze-url")
def getImage(url: str):
    origDir = os.getcwd()
    os.chdir("FALdetector")
    session = str(uuid.uuid4())
    filePath = url.split('/')[-1]
    r = requests.get(url, allow_redirects=True)
    contents = r.content
    open(filePath, 'wb').write(contents)
    scriptPath = "local_detector.py"
    weightsPath = os.path.join("weights", "local.pth")
    if not os.path.exists(session):
        os.makedirs(session)
    analyze_cmd = (
        "python3 "
        + scriptPath
        + " --input_path "
        + filePath
        + " --model_path "
        + weightsPath
        + " --dest_folder "
        + session
        + " --no_crop"
    )
    p = subprocess.Popen(analyze_cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    image = None
    heatmap = os.path.join(session, "heatmap.jpg")
    if os.path.isfile(heatmap):
        with open(heatmap, "rb") as fh:
            image = fh.read()
    # Cleanup
    os.remove(filePath)
    shutil.rmtree(session)
    os.chdir(origDir)
    if image:
        return StreamingResponse(base64.b64encode(BytesIO(image).getvalue()), media_type="image/jpeg;base64")
    else:
        return StreamingResponse(base64.b64encode(BytesIO(contents).getvalue()), media_type="image/jpeg;base64")
