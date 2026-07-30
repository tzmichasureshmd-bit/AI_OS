import os
from dotenv import load_dotenv

load_dotenv()

# Groq API (FREE - get key from https://console.groq.com)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-free-groq-api-key-here")

# AI Model Settings
AI_MODEL = "llama-3.3-70b-versatile"
AI_TEMPERATURE = 0.7

# Twilio (Real Phone Calls)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Deepgram (Fast STT ~300ms)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")

# ElevenLabs (Human-like TTS)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Server Public URL (ngrok for local dev)
SERVER_PUBLIC_URL = os.getenv("SERVER_PUBLIC_URL", "http://localhost:8000")

# Call Settings
MAX_CALL_DURATION_SECONDS = 180
LANGUAGE = "en"

# Lead Scoring Thresholds
HOT_LEAD_SCORE = 7
WARM_LEAD_SCORE = 4
COLD_LEAD_SCORE = 0

# Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'leads.db')}"

# Server
HOST = "0.0.0.0"
PORT = 8000
