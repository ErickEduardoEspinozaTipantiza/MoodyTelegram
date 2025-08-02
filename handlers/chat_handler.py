import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import BotStates
from utils.helpers import load_user_session, save_user_session
from services.ollama_client import ollama_client
from services.pdf_generator import generate_conversation_summary_pdf

logger = logging.getLogger(__name__)

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la conversación con el LLM"""
    user_id = update.effective_user.id
    user_session = load_user_session(user_id)
    
    if user_session.get("state") != BotStates.CHAT_WITH_LLM:
        await update.message.reply_text(
            "💬 Para usar el chat, primero completa el análisis escribiendo /start"
        )
        return
    
    user_message = update.message.text
    
    # Verificar si el usuario quiere generar un resumen
    if user_message.lower().strip() in ['/resumen', '/summary', 'resumen', 'generar resumen', 'resumen de conversacion', 'finalizar']:
        await generate_conversation_summary(update, context)
        return
    
    # Mostrar indicador de escritura
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Preparar contexto para el LLM
        context_info = prepare_chat_context(user_session)
        
        # Generar respuesta con Ollama
        response = await ollama_client.generate_response(user_message, context_info)
        
        if response:
            # Dividir respuesta si es muy larga
            if len(response) > 4000:
                # Telegram tiene límite de 4096 caracteres
                parts = split_long_message(response)
                for part in parts:
                    await update.message.reply_text(part)
            else:
                # Agregar botones de acción después de algunas conversaciones
                reply_markup = None
                chat_count = len(user_session.get("chat_history", []))
                
                if chat_count >= 3 and chat_count % 5 == 0:  # Cada 5 mensajes después del 3ro
                    keyboard = [
                        [InlineKeyboardButton("📋 Generar resumen de conversación", callback_data="action_generate_summary")],
                        [InlineKeyboardButton("🔄 Nueva consulta", callback_data="action_restart")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(response, reply_markup=reply_markup)
            
            # Guardar la conversación en la sesión
            if "chat_history" not in user_session:
                user_session["chat_history"] = []
            
            user_session["chat_history"].append({
                "user": user_message,
                "bot": response,
                "timestamp": update.message.date.isoformat()
            })
            
            # Mantener solo las últimas 15 conversaciones para no saturar
            if len(user_session["chat_history"]) > 15:
                user_session["chat_history"] = user_session["chat_history"][-15:]
            
            save_user_session(user_id, user_session)
            
        else:
            await update.message.reply_text(
                "❌ Lo siento, no pude generar una respuesta en este momento. "
                "Por favor, intenta nuevamente.\n\n"
                "💡 Puedes escribir '/resumen' para generar un resumen de nuestra conversación."
            )
            
    except Exception as e:
        logger.error(f"Error en chat con usuario {user_id}: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error durante nuestra conversación. "
            "Por favor, intenta nuevamente en un momento.\n\n"
            "💡 Puedes escribir '/resumen' para generar un resumen de lo que hemos hablado."
        )

async def generate_conversation_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera un resumen completo de la conversación y análisis"""
    user_id = update.effective_user.id
    user_session = load_user_session(user_id)
    
    chat_history = user_session.get("chat_history", [])
    
    if len(chat_history) < 2:
        await update.message.reply_text(
            "💬 Necesitas tener al menos 2 intercambios de conversación para generar un resumen.\n"
            "Continúa hablando conmigo y luego escribe '/resumen' cuando quieras el análisis final."
        )
        return
    
    # Mostrar mensaje de procesamiento
    processing_msg = await update.message.reply_text(
        "🔄 Generando resumen completo de nuestra conversación y análisis... "
        "Esto puede tomar unos momentos."
    )
    
    try:
        # Preparar toda la información para el resumen
        full_context = prepare_full_context_for_summary(user_session)
        
        # Generar resumen con Ollama
        summary_prompt = create_summary_prompt(user_session, chat_history)
        summary = await ollama_client.generate_response(summary_prompt, full_context)
        
        if summary:
            # Guardar el resumen en la sesión
            user_session["conversation_summary"] = summary
            user_session["summary_generated_at"] = update.message.date.isoformat()
            save_user_session(user_id, user_session)
            
            # Generar PDF del resumen completo
            summary_pdf_path = await generate_conversation_summary_pdf(user_session, summary)
            if summary_pdf_path:
                user_session["summary_pdf_path"] = summary_pdf_path
                save_user_session(user_id, user_session)
            
            # Mostrar el resumen y opciones
            await show_conversation_summary(update, context, summary, processing_msg)
        else:
            await processing_msg.edit_text(
                "❌ No pude generar el resumen completo. "
                "Por favor, intenta nuevamente en un momento."
            )
    
    except Exception as e:
        logger.error(f"Error generando resumen para usuario {user_id}: {e}")
        await processing_msg.edit_text(
            "❌ Ocurrió un error al generar el resumen. "
            "Por favor, intenta nuevamente."
        )

def create_summary_prompt(user_session: dict, chat_history: list) -> str:
    """Crea el prompt para generar el resumen completo"""
    therapy_type = user_session.get("therapy_name", "No especificado")
    emotion = user_session.get("emotion_detected", "No detectado")
    
    # Construir historial de conversación
    conversation_text = ""
    for i, exchange in enumerate(chat_history, 1):
        conversation_text += f"\n{i}. Usuario: {exchange['user']}\n"
        conversation_text += f"   Respuesta: {exchange['bot']}\n"
    
    prompt = f"""
Como psicólogo clínico profesional, analiza la siguiente información y genera un resumen con recomendaciones específicas y aplicables:

INFORMACIÓN INICIAL:
- Tipo de terapia seleccionada: {therapy_type}
- Emoción detectada por voz: {emotion}

CONVERSACIÓN COMPLETA:
{conversation_text}

Por favor, genera un ANÁLISIS PROFESIONAL ESTRUCTURADO que incluya:

1. **EVALUACIÓN CLÍNICA**: Identifica patrones emocionales, pensamientos recurrentes y comportamientos observados durante la conversación.

2. **DIAGNÓSTICO SITUACIONAL**: Análisis de factores desencadenantes, recursos personales disponibles y áreas de vulnerabilidad.

3. **INTERVENCIONES ESPECÍFICAS**: Recomendaciones concretas con técnicas aplicables:
   - Técnicas de regulación emocional específicas (con pasos detallados)
   - Ejercicios prácticos para implementar en casa
   - Estrategias de afrontamiento personalizadas
   - Cronograma semanal de actividades terapéuticas

4. **PLAN DE SEGUIMIENTO**: 
   - Objetivos terapéuticos específicos a corto plazo (1-4 semanas)
   - Indicadores de progreso medibles
   - Frecuencia de sesiones recomendada
   - Criterios para derivación a especialista

5. **RECURSOS COMPLEMENTARIOS**: 
   - Aplicaciones móviles específicas para el caso
   - Lecturas recomendadas
   - Técnicas de mindfulness adaptadas al perfil
   - Ejercicios físicos terapéuticos

6. **ALERTAS CLÍNICAS**: Señales de alarma que requieren atención inmediata profesional.

IMPORTANTE: Las recomendaciones deben ser:
- Específicas y medibles (no genéricas)
- Aplicables inmediatamente
- Basadas en evidencia científica
- Adaptadas al perfil emocional del usuario

Usa terminología profesional pero accesible. El análisis será revisado por profesionales de salud mental.
"""
    return prompt

def prepare_full_context_for_summary(user_session: dict) -> str:
    """Prepara el contexto completo para el resumen"""
    context_parts = []
    
    # Información del cuestionario
    answers = user_session.get("answers", [])
    questions = user_session.get("questions", [])
    
    if answers and questions:
        context_parts.append("RESPUESTAS DEL CUESTIONARIO INICIAL:")
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            context_parts.append(f"{i}. {q}")
            context_parts.append(f"   R: {a}")
    
    # Información emocional
    emotion_desc = user_session.get("emotion_description", "")
    if emotion_desc:
        context_parts.append(f"\nANÁLISIS EMOCIONAL POR VOZ: {emotion_desc}")
    
    return "\n".join(context_parts)

async def show_conversation_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, summary: str, message_to_edit):
    """Muestra el resumen de la conversación con opciones"""
    
    # Truncar el resumen si es muy largo para Telegram
    if len(summary) > 3500:
        summary_preview = summary[:3500] + "\n\n[Resumen completo disponible en PDF]"
    else:
        summary_preview = summary
    
    final_message = f"""
📋 **RESUMEN COMPLETO DE LA SESIÓN**

{summary_preview}

---
✅ **Tu resumen completo está listo**

¿Qué te gustaría hacer?
"""
    
    keyboard = [
        [InlineKeyboardButton("📧 Enviar resumen por email", callback_data="action_send_summary_email")],
        [InlineKeyboardButton("📥 Descargar resumen PDF", callback_data="action_download_summary")],
        [InlineKeyboardButton("💬 Continuar conversación", callback_data="action_continue_chat")],
        [InlineKeyboardButton("🔄 Nueva consulta", callback_data="action_restart")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message_to_edit.edit_text(
        final_message, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

def prepare_chat_context(user_session: dict) -> str:
    """Prepara el contexto para el chat basado en el análisis previo"""
    context_parts = []
    
    # Información del tipo de terapia
    therapy_name = user_session.get("therapy_name")
    if therapy_name:
        context_parts.append(f"El usuario está interesado en {therapy_name}")
    
    # Información emocional
    emotion = user_session.get("emotion_detected")
    if emotion:
        emotion_description = user_session.get("emotion_description", "")
        context_parts.append(f"Análisis emocional: {emotion_description}")
    
    # Algunas respuestas relevantes del cuestionario
    answers = user_session.get("answers", [])
    if answers:
        # Tomar las primeras 2 respuestas como contexto
        relevant_answers = answers[:2]
        context_parts.append(f"Respuestas previas del usuario: {'; '.join(relevant_answers)}")
    
    return " | ".join(context_parts) if context_parts else ""

def split_long_message(message: str, max_length: int = 4000) -> list:
    """Divide un mensaje largo en partes más pequeñas"""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    current_part = ""
    sentences = message.split('. ')
    
    for sentence in sentences:
        if len(current_part + sentence + '. ') <= max_length:
            current_part += sentence + '. '
        else:
            if current_part:
                parts.append(current_part.strip())
                current_part = sentence + '. '
            else:
                # Si una sola oración es muy larga, dividirla por palabras
                words = sentence.split()
                temp_part = ""
                for word in words:
                    if len(temp_part + word + ' ') <= max_length:
                        temp_part += word + ' '
                    else:
                        if temp_part:
                            parts.append(temp_part.strip())
                            temp_part = word + ' '
                        else:
                            # Si una palabra es más larga que el límite, dividirla
                            parts.append(word[:max_length])
                            temp_part = word[max_length:] + ' '
                if temp_part:
                    current_part = temp_part + '. '
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts
