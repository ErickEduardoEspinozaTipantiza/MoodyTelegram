from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import BotStates, THERAPY_TYPES
from config.therapy_questions import THERAPY_QUESTIONS, THERAPY_INTRO
from utils.helpers import load_user_session, save_user_session

async def handle_therapy_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección del tipo de terapia"""
    query = update.callback_query
    await query.answer()
    
    therapy_type = query.data.replace("therapy_", "")
    user_id = update.effective_user.id
    
    if therapy_type not in THERAPY_TYPES:
        await query.edit_message_text("❌ Tipo de terapia no válido.")
        return
    
    # Actualizar sesión del usuario
    user_session = load_user_session(user_id)
    user_session.update({
        "state": BotStates.ANSWERING_QUESTIONS,
        "therapy_type": therapy_type,
        "therapy_name": THERAPY_TYPES[therapy_type],
        "questions": THERAPY_QUESTIONS[therapy_type],
        "answers": [],
        "current_question": 0
    })
    save_user_session(user_id, user_session)
    
    # Mostrar introducción y primera pregunta
    intro_message = f"""
✅ **{THERAPY_TYPES[therapy_type]}**

{THERAPY_INTRO[therapy_type]}

Responderás **6 preguntas**. Tómate tu tiempo para reflexionar sobre cada una.

**Pregunta 1 de 6:**
{THERAPY_QUESTIONS[therapy_type][0]}
"""
    
    await query.edit_message_text(intro_message, parse_mode='Markdown')

async def handle_question_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las respuestas a las preguntas del cuestionario"""
    user_id = update.effective_user.id
    user_session = load_user_session(user_id)
    
    if user_session.get("state") != BotStates.ANSWERING_QUESTIONS:
        await update.message.reply_text("❌ No hay un cuestionario activo. Escribe /start para comenzar.")
        return
    
    # Guardar respuesta actual
    answer = update.message.text
    user_session["answers"].append(answer)
    user_session["current_question"] += 1
    
    current_q = user_session["current_question"]
    total_questions = len(user_session["questions"])
    
    if current_q < total_questions:
        # Mostrar siguiente pregunta
        next_question = user_session["questions"][current_q]
        message = f"""
✅ **Respuesta guardada**

**Pregunta {current_q + 1} de {total_questions}:**
{next_question}
"""
        await update.message.reply_text(message, parse_mode='Markdown')
        save_user_session(user_id, user_session)
        
    else:
        # Todas las preguntas respondidas, solicitar audio
        user_session["state"] = BotStates.RECORDING_VOICE
        save_user_session(user_id, user_session)
        
        message = """
🎉 **¡Excelente! Has completado todas las preguntas.**

Ahora necesito que grabes un **audio breve (máximo 10 segundos)** expresando cómo te sientes en este momento.

🎤 **Instrucciones para el audio:**
• Habla de forma natural
• Expresa tus emociones actuales
• No importa el idioma que uses
• Máximo 10 segundos

Presiona el botón de micrófono en Telegram y graba tu mensaje de voz.
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
