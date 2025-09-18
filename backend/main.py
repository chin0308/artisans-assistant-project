import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import vision
from google.cloud import aiplatform

# ======================
# Load ENV Vars
# ======================
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0454209804")
LOCATION = "us-central1"

TEXT_MODEL = os.getenv(
    "VERTEX_MODEL",
    f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/text-bison"
)

IMAGE_MODEL = os.getenv(
    "VERTEX_IMAGE_MODEL",
    f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/image-bison"
)

# Init Google AI Clients
vision_client = vision.ImageAnnotatorClient()
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# ======================
# FastAPI App Setup
# ======================
app = FastAPI(title="Artisan Assistant API")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in hackathon, keep open
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Schemas
# ======================
class PostRequest(BaseModel):
    description: str

class PostResponse(BaseModel):
    generated_post: str

# ======================
# Routes
# ======================

@app.get("/")
def root():
    return {"status": "ok", "message": "Artisan Assistant API is running 🚀"}

# ---- 1. Image Analysis (Vision API)
@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image = vision.Image(content=content)

        response = vision_client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]

        return {"labels": labels}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- 2. Generate Social Post (Vertex AI Text)
@app.post("/generate/post", response_model=PostResponse)
async def generate_post(req: PostRequest):
    try:
        # Example: use Vertex AI text model
        text_model = aiplatform.TextGenerationModel(model_name=TEXT_MODEL)

        prompt = f"Write an Instagram-style post for this artisan product: {req.description}"
        response = text_model.predict(prompt=prompt, temperature=0.7, max_output_tokens=256)

        return {"generated_post": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- 3. Generate Image Mockup (Vertex AI Image)
@app.post("/generate/image")
async def generate_image(req: PostRequest):
    try:
        image_model = aiplatform.ImageGenerationModel(model_name=IMAGE_MODEL)

        prompt = f"Generate a modern product photo mockup of: {req.description}"
        response = image_model.predict(prompt=prompt)

        return {"image_url": response.generated_images[0].uri}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    