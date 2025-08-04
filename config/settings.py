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

# Emociones detectables (modelo entrenado)
EMOTIONS = {
    "anger": "Ira",
    "disgust": "Disgusto",
    "fear": "Miedo",
    "happiness": "Felicidad",
    "neutral": "Neutral",
    "sadness": "Tristeza"
}

# Doctores especialistas por tipo de terapia
SPECIALISTS = {
    "familiar": {
        "name": "Dra. María Elena Vásquez",
        "title": "Especialista en Terapia Familiar Sistémica",
        "credentials": "Psicóloga Clínica, Magíster en Terapia Familiar",
        "experience": "15 años de experiencia en dinámicas familiares",
        "email": "crisgeopro2003@gmail.com",
        "phone": "+593 98 765 4321",
        "specialties": ["Conflictos familiares", "Comunicación familiar", "Crianza positiva"]
    },
    "pareja": {
        "name": "Dr. Carlos Alberto Mendoza",
        "title": "Especialista en Terapia de Pareja",
        "credentials": "Psicólogo Clínico, Certificado en Terapia de Pareja Gottman",
        "experience": "12 años especializándose en relaciones de pareja",
        "email": "crisgeopro2003@gmail.com",
        "phone": "+593 99 876 5432",
        "specialties": ["Conflictos de pareja", "Comunicación afectiva", "Infidelidad"]
    },
    "individual": {
        "name": "Dra. Ana Sofía Herrera",
        "title": "Especialista en Psicología Clínica Individual",
        "credentials": "Psicóloga Clínica, Magíster en Psicoterapia Cognitivo-Conductual",
        "experience": "18 años en psicoterapia individual",
        "email": "crisgeopro2003@gmail.com",
        "phone": "+593 97 654 3210",
        "specialties": ["Ansiedad y depresión", "Autoestima", "Crecimiento personal"]
    },
    "adolescentes": {
        "name": "Dr. Roberto Andrés Castro",
        "title": "Especialista en Psicología del Adolescente",
        "credentials": "Psicólogo Clínico, Especialista en Psicología del Desarrollo",
        "experience": "10 años trabajando con adolescentes",
        "email": "crisgeopro2003@gmail.com",
        "phone": "+593 96 543 2109",
        "specialties": ["Problemas de conducta", "Identidad adolescente", "Presión académica"]
    }
}
