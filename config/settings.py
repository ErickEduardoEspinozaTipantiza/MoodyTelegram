import os
from dotenv import load_dotenv

load_dotenv()

# Configuración del bot de Telegram
TELEGRAM_BOT_TOKEN = "8293226970:AAHns7nkSeL4SFHbmH7K6YOlglq6YAwgL1Q"

# Configuración de Ollama
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = "llama3"

# Configuración de email
EMAIL_USER = os.getenv("EMAIL_USER", "crisgeopro2003@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Rutas de archivos
import os
MODELS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TEMP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")

# Configuración de audio
MAX_AUDIO_DURATION = 10  # segundos
AUDIO_SAMPLE_RATE = 16000

# Estados del bot
class BotStates:
    START = "start"
    SELECTING_THERAPY = "selecting_therapy"
    ANSWERING_QUESTIONS = "answering_questions"
    RECORDING_VOICE = "recording_voice"
    PROCESSING_RESULTS = "processing_results"
    CHAT_WITH_LLM = "chat_with_llm"

# Tipos de terapia disponibles
THERAPY_TYPES = {
    "familiar": "Terapia Familiar",
    "pareja": "Terapia de Pareja", 
    "individual": "Terapia Individual",
    "adolescentes": "Terapia para Adolescentes"
}

# Emociones detectables
EMOTIONS = {
    "sad": "Tristeza",
    "angry": "Ira",
    "anxious": "Ansiedad",
    "calm": "Calma",
    "happy": "Felicidad",
    "fear": "Miedo",
    "neutral": "Neutral"
}
