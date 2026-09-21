import whisper
import logging
import os
import imageio_ffmpeg

# Inject ffmpeg from imageio_ffmpeg into PATH so whisper can find it
os.environ["PATH"] += os.pathsep + os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

logger = logging.getLogger("WhisperService")

# Load model globally to avoid loading it on every request
# Using "base" for faster CPU performance locally
try:
    logger.info("Loading Whisper model 'base'...")
    model = whisper.load_model("base")
    logger.info("Whisper model loaded.")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {e}")
    model = None

def transcribe_audio_file(file_path: str) -> str:
    if not model:
        raise Exception("Whisper model is not loaded.")
        
    try:
        # Run transcription (whisper natively uses ffmpeg to load any format)
        result = model.transcribe(file_path)
        return result["text"].strip()
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise e
