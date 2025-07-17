"""
Media Processing Tools for AgentSpring
Includes audio transcription, image analysis, and text extraction tools
"""
from typing import List, Optional
from . import tool

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import textract
    TEXTRACT_AVAILABLE = True
except ImportError:
    TEXTRACT_AVAILABLE = False

@tool("transcribe_audio", "Transcribe audio to text using Whisper", permissions=[])
def transcribe_audio(audio_path: str):
    if not WHISPER_AVAILABLE:
        raise Exception("Whisper not installed")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return {"text": result["text"], "audio_path": audio_path}

@tool("analyze_image", "Analyze an image using Pillow", permissions=[])
def analyze_image(image_path: str):
    if not PIL_AVAILABLE:
        raise Exception("Pillow not installed")
    img = Image.open(image_path)
    width, height = img.size
    mode = img.mode
    format = img.format
    return {
        "width": width,
        "height": height,
        "mode": mode,
        "format": format,
        "image_path": image_path
    } 