import requests
import json
import logging
from typing import Optional
from config.settings import OLLAMA_API_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.api_url = OLLAMA_API_URL
        self.model = OLLAMA_MODEL
        self.is_available = False
        self.check_availability()
    
    def check_availability(self):
        """Verifica si Ollama está disponible"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_available = True
                logger.info("Ollama está disponible")
            else:
                logger.warning(f"Ollama no disponible, código: {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"No se pudo conectar con Ollama: {e}")
            self.is_available = False
    
    async def generate_response(self, prompt: str, context: str = "") -> Optional[str]:
        """Genera una respuesta usando Ollama"""
        if not self.is_available:
            self.check_availability()
            if not self.is_available:
                return self._get_fallback_response(prompt)
        
        try:
            # Construir el prompt completo con contexto
            full_prompt = self._build_prompt(prompt, context)
            
            # Configurar la petición
            data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            # Hacer la petición con timeout aumentado
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=data,
                timeout=60  # Aumentado de 30 a 60 segundos
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Error en Ollama: {response.status_code}")
                return self._get_fallback_response(prompt)
                
        except requests.exceptions.Timeout:
            logger.warning("Timeout conectando con Ollama, usando respuesta de respaldo")
            return self._get_fallback_response(prompt)
        except requests.RequestException as e:
            logger.error(f"Error conectando con Ollama: {e}")
            return self._get_fallback_response(prompt)
        except Exception as e:
            logger.error(f"Error inesperado con Ollama: {e}")
            return self._get_fallback_response(prompt)
    
    def _build_prompt(self, user_message: str, context: str = "") -> str:
        """Construye el prompt para Ollama con contexto de terapia"""
        
        # Detectar si es un prompt de resumen
        if "ANÁLISIS EMOCIONAL GENERAL" in user_message or "Como especialista en salud mental" in user_message:
            # Para resúmenes profesionales, usar un prompt más estructurado
            return f"{user_message}\n\nPor favor, proporciona un análisis profesional detallado y estructurado:"
        
        # Para conversación normal
        system_prompt = """
Eres un asistente empático especializado en apoyo emocional y bienestar mental. 
Tu papel es:

1. Escuchar activamente y validar las emociones del usuario
2. Hacer preguntas reflexivas que ayuden al autoconocimiento
3. Ofrecer perspectivas positivas y estrategias de afrontamiento
4. Mantener un tono cálido, comprensivo y profesional
5. NO dar diagnósticos médicos ni reemplazar terapia profesional

Directrices importantes:
- Usa un lenguaje sencillo y empático
- Haz preguntas abiertas para fomentar la reflexión
- Valida las emociones sin juzgar
- Sugiere técnicas simples de bienestar cuando sea apropiado
- Recuerda que eres un apoyo, no un terapeuta

"""
        
        if context:
            system_prompt += f"\nContexto del usuario: {context}\n"
        
        return f"{system_prompt}\n\nUsuario: {user_message}\n\nRespuesta empática:"
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Respuestas de respaldo cuando Ollama no está disponible"""
        fallback_responses = [
            "Entiendo cómo te sientes. Es completamente normal tener estos sentimientos. ¿Te gustaría contarme más sobre lo que estás experimentando?",
            
            "Gracias por compartir esto conmigo. Es valiente de tu parte expresar tus emociones. ¿Hay algo específico que te esté preocupando en este momento?",
            
            "Te escucho y valido lo que sientes. Cada emoción tiene su propósito. ¿Has notado qué situaciones o pensamientos desencadenan estos sentimientos?",
            
            "Aprecio tu confianza al compartir esto. Es importante reconocer nuestras emociones. ¿Qué crees que podrías necesitar en este momento para sentirte mejor?",
            
            "Lo que sientes es válido e importante. Muchas personas pasan por experiencias similares. ¿Te ayudaría hablar sobre algunas estrategias para manejar estos sentimientos?"
        ]
        
        # Seleccionar respuesta basada en palabras clave
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['triste', 'deprimido', 'solo']):
            return "Entiendo que te sientes triste. Es una emoción humana natural. ¿Te gustaría contarme qué está contribuyendo a esta tristeza? A veces hablar sobre ello puede ayudar a aliviarlo."
        
        elif any(word in prompt_lower for word in ['ansioso', 'preocupado', 'nervioso']):
            return "La ansiedad puede ser abrumadora. Es importante recordar que estos sentimientos pasarán. ¿Has intentado alguna técnica de respiración profunda? También me gustaría saber qué específicamente te está causando esta ansiedad."
        
        elif any(word in prompt_lower for word in ['enojado', 'furioso', 'molesto']):
            return "Es comprensible sentir enojo a veces. Esta emoción puede indicar que algo importante para ti ha sido afectado. ¿Puedes identificar qué causó este sentimiento? Hablar sobre ello puede ayudarte a procesarlo."
        
        elif any(word in prompt_lower for word in ['feliz', 'contento', 'bien']):
            return "Me alegra saber que te sientes bien. Es maravilloso cuando podemos experimentar emociones positivas. ¿Qué está contribuyendo a este bienestar? Reconocer estos momentos puede ayudarnos a cultivar más de ellos."
        
        else:
            return fallback_responses[len(prompt) % len(fallback_responses)]

# Instancia global del cliente
ollama_client = OllamaClient()
