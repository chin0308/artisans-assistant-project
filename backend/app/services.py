"""
AI Services: This file integrates OpenAI + Google APIs.
"""

import openai
import os
from google.cloud import speech, vision
from google.protobuf.json_format import MessageToDict
import base64

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- AI Caption Generator ---
def generate_caption(description: str) -> dict:
    """
    Use OpenAI GPT to generate a caption + hashtags.
    """
    prompt = f"""
    You are a social media marketer for artisans. 
    Write a catchy Instagram caption and 5 hashtags 
    for this artisan product description: "{description}".
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You help artisans market their craft."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )
    text = response["choices"][0]["message"]["content"]

    # crude split (for demo) → can be improved
    parts = text.split("#")
    caption = parts[0].strip()
    hashtags = [("#" + tag.strip()).split()[0] for tag in parts[1:6]]

    return {"caption": caption, "hashtags": hashtags}


# --- Mockup Generator (Stub + Extendable) ---
def generate_mockup(product_type: str) -> str:
    """
    For demo, return a placeholder mockup image.
    (In hackathon, can be replaced with Stable Diffusion API)
    """
    return f"https://dummyimage.com/600x400/eee/000.png&text={product_type}+in+Modern+Kitchen"


# --- Voice to Text ---
def process_voice_to_text(file_path: str) -> str:
    """
    Uses Google Cloud Speech-to-Text to transcribe audio.
    """
    client = speech.SpeechClient()
    with open(file_path, "rb") as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="hi-IN"  # Hindi input
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript or "No speech detected"
# --- Image Analysis ---
def analyze_image(file_path: str) -> dict:
    """
    Uses Google Cloud Vision to analyze image and extract labels.
    """
    client = vision.ImageAnnotatorClient()
    with open(file_path, "rb") as f:
        image_content = f.read()

    image = vision.Image(content=image_content)
    response = client.label_detection(image=image)
    labels = [label.description for label in response.label_annotations]
    return {"labels": labels}