from fastapi import APIRouter, UploadFile, File, Form
from app.models import GeneratePostRequest, GeneratePostResponse
from app.services import generate_caption, generate_mockup, process_voice_to_text
import shutil
import uuid
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/ping")
def ping():
    return {"msg": "pong"}

# Upload image
@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_name": file.filename, "url": f"/static/{file.filename}"}

# Upload voice → transcript
@router.post("/upload/voice")
async def upload_voice(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    transcript = process_voice_to_text(save_path)
    return {"transcript": transcript}

# Generate AI Post
@router.post("/generate/post", response_model=GeneratePostResponse)
async def generate_post(request: GeneratePostRequest):
    ai_result = generate_caption(request.description)
    mockup_url = generate_mockup("Clay Pot")
    return GeneratePostResponse(
        caption=ai_result["caption"],
        hashtags=ai_result["hashtags"],
        image_url="https://dummyimage.com/600x400/ccc/000.png&text=Uploaded+Product",
        mockup_url=mockup_url
    )
