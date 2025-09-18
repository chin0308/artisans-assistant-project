from pydantic import BaseModel
from typing import List

class UploadImageRequest(BaseModel):
    artisan_name: str
    product_type: str

class GeneratePostRequest(BaseModel):
    description: str  # text from user or voice transcript

class GeneratePostResponse(BaseModel):
    caption: str
    hashtags: List[str]
    image_url: str
    mockup_url: str
