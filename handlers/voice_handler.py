import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import BotStates, MAX_AUDIO_DURATION
from utils.helpers import (
    load_user_session, 
    save_user_session, 
    get_temp_audio_path,
    validate_audio_file,
    get_emotion_emoji
)
from services.emotion_analyzer import emotion_analyzer
from services.pdf_generator import generate_report_pdf

logger = logging.getLogger(__name__)

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los mensajes de voz para análisis de emociones"""
    user_id = update.effective_user.id
    user_session = load_user_session(user_id)
    
    if user_session.get("state") != BotStates.RECORDING_VOICE:
        await update.message.reply_text(
            "🎤 Para usar el análisis de voz, primero completa el cuestionario escribiendo /start"
        )
        return
    
    voice = update.message.voice
    
    # Verificar duración del audio
    if voice.duration > MAX_AUDIO_DURATION:
        await update.message.reply_text(
            f"⏰ El audio es muy largo. Por favor, graba un mensaje de máximo {MAX_AUDIO_DURATION} segundos."
        )
        return
    
    try:
        # Mostrar mensaje de procesamiento
        processing_msg = await update.message.reply_text("🔄 Analizando tu voz... Por favor espera.")
        
        # Descargar archivo de voz
        audio_path = get_temp_audio_path(user_id)
        voice_file = await context.bot.get_file(voice.file_id)
        await voice_file.download_to_drive(audio_path)
        
        # Validar archivo
        if not validate_audio_file(audio_path):
            await processing_msg.edit_text("❌ Error al procesar el audio. Intenta grabar nuevamente.")
            return
        
        # Analizar emoción
        emotion, confidence = emotion_analyzer.predict_emotion(audio_path)
        emotion_description = emotion_analyzer.get_emotion_description(emotion, confidence)
        
        # Guardar resultados en la sesión
        user_session.update({
            "state": BotStates.PROCESSING_RESULTS,
            "emotion_detected": emotion,
            "emotion_confidence": confidence,
            "emotion_description": emotion_description
        })
        save_user_session(user_id, user_session)
        
        # Generar reporte PDF
        pdf_path = await generate_report_pdf(user_session)
        if pdf_path:
            user_session["pdf_path"] = pdf_path
            save_user_session(user_id, user_session)
        
        # Mostrar resultados y permitir descarga/email
        await show_analysis_results(update, context, processing_msg)
        
        # Esperar un momento y luego cambiar a estado de chat
        await asyncio.sleep(2)  # Esperar 2 segundos para que el usuario vea los resultados
        
        # Automáticamente cambiar a estado de chat después de mostrar resultados
        user_session["state"] = BotStates.CHAT_WITH_LLM
        save_user_session(user_id, user_session)
        
        # Enviar mensaje informativo sobre el chat
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="""
💬 **¡Perfecto! Ya tienes tu análisis completo**

**Ahora puedes conversar conmigo libremente:**
• Pregúntame sobre tu estado emocional
• Pide consejos específicos sobre tu situación
• Explora temas relacionados a tu bienestar
• Comparte cómo te sientes ahora

**Comandos útiles:**
• `/resumen` - Generar análisis completo de nuestra conversación
• `/start` - Comenzar un nuevo análisis desde cero

✨ **Escribe cualquier mensaje para empezar nuestra conversación!**
""",
            parse_mode='Markdown'
        )
        
        # Limpiar archivo de audio temporal
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        logger.error(f"Error procesando voz del usuario {user_id}: {e}")
        await processing_msg.edit_text(
            "❌ Ocurrió un error al analizar tu voz. Intenta nuevamente."
        )

async def show_analysis_results(update: Update, context: ContextTypes.DEFAULT_TYPE, message_to_edit):
    """Muestra los resultados del análisis completo"""
    user_id = update.effective_user.id
    user_session = load_user_session(user_id)
    
    emotion = user_session.get("emotion_detected", "neutral")
    emotion_description = user_session.get("emotion_description", "")
    therapy_name = user_session.get("therapy_name", "")
    therapy_type = user_session.get("therapy_type", "individual")
    
    emotion_emoji = get_emotion_emoji(emotion)
    
    # Obtener información del especialista
    from config.settings import SPECIALISTS
    specialist = SPECIALISTS.get(therapy_type, SPECIALISTS["individual"])
    
    results_message = f"""
🎯 **RESULTADOS DEL ANÁLISIS COMPLETO**

📋 **Tipo de terapia:** {therapy_name}
{emotion_emoji} **Análisis emocional:** {emotion_description}

✅ **Tu reporte está listo**

El análisis completo incluye:
• Tus respuestas al cuestionario personalizado
• Análisis de emociones por voz con IA
• Recomendaciones profesionales específicas
• Contacto de especialista de referencia

👨‍⚕️ **ESPECIALISTA ASIGNADO:**
**{specialist['name']}**
{specialist['title']}
📧 {specialist['email']}
📱 {specialist['phone']}
⭐ {specialist['experience']}

¿Qué te gustaría hacer ahora?
"""
    
    keyboard = [
        [InlineKeyboardButton("📧 Enviar por email al especialista", callback_data="action_send_email")],
        [InlineKeyboardButton("📥 Descargar PDF", callback_data="action_download_pdf")],
        [InlineKeyboardButton("💬 Conversar con IA", callback_data="action_chat_llm")],
        [InlineKeyboardButton("🔄 Nuevo análisis", callback_data="action_restart")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message_to_edit.edit_text(
        results_message, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )
