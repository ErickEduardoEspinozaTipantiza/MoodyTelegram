import os
import json
import logging
from datetime import datetime
from config.settings import DATA_PATH, TEMP_PATH

logger = logging.getLogger(__name__)

def create_temp_directory():
    """Crea el directorio temporal si no existe"""
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

def load_user_session(user_id: int) -> dict:
    """Carga la sesión del usuario desde el archivo JSON"""
    session_file = os.path.join(DATA_PATH, f"session_{user_id}.json")
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando sesión del usuario {user_id}: {e}")
    
    return {"user_id": user_id, "created_at": datetime.now().isoformat()}

def save_user_session(user_id: int, session_data: dict):
    """Guarda la sesión del usuario en el archivo JSON"""
    session_file = os.path.join(DATA_PATH, f"session_{user_id}.json")
    session_data["updated_at"] = datetime.now().isoformat()
    
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando sesión del usuario {user_id}: {e}")

def clear_user_session(user_id: int):
    """Limpia la sesión del usuario"""
    session_file = os.path.join(DATA_PATH, f"session_{user_id}.json")
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
        except Exception as e:
            logger.error(f"Error eliminando sesión del usuario {user_id}: {e}")

def format_user_answers(answers: list, questions: list) -> str:
    """Formatea las respuestas del usuario para el reporte"""
    formatted = ""
    for i, (question, answer) in enumerate(zip(questions, answers), 1):
        formatted += f"{i}. {question}\n"
        formatted += f"   Respuesta: {answer}\n\n"
    return formatted

def get_temp_audio_path(user_id: int) -> str:
    """Genera la ruta del archivo de audio temporal"""
    return os.path.join(TEMP_PATH, f"audio_{user_id}.ogg")

def get_temp_pdf_path(user_id: int) -> str:
    """Genera la ruta del archivo PDF temporal"""
    return os.path.join(TEMP_PATH, f"reporte_{user_id}.pdf")

def cleanup_temp_files(user_id: int):
    """Limpia los archivos temporales del usuario"""
    audio_path = get_temp_audio_path(user_id)
    pdf_path = get_temp_pdf_path(user_id)
    
    for file_path in [audio_path, pdf_path]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error eliminando archivo temporal {file_path}: {e}")

def validate_audio_file(file_path: str) -> bool:
    """Valida que el archivo de audio sea válido"""
    if not os.path.exists(file_path):
        return False
    
    # Verificar que el archivo no esté vacío
    if os.path.getsize(file_path) == 0:
        return False
    
    return True

def get_emotion_emoji(emotion: str) -> str:
    """Retorna el emoji correspondiente a la emoción"""
    emotion_emojis = {
        "sad": "😢",
        "angry": "😠", 
        "anxious": "😰",
        "calm": "😌",
        "happy": "😊",
        "fear": "😨",
        "neutral": "😐"
    }
    return emotion_emojis.get(emotion.lower(), "🤔")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Trunca el texto si es muy largo"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
