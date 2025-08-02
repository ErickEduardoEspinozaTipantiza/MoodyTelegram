from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import BotStates, THERAPY_TYPES
from utils.helpers import load_user_session, save_user_session, clear_user_session

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    user = update.effective_user
    user_id = user.id
    
    # Limpiar sesión anterior
    clear_user_session(user_id)
    
    # Crear nueva sesión
    session_data = {
        "user_id": user_id,
        "username": user.username,
        "first_name": user.first_name,
        "state": BotStates.START
    }
    save_user_session(user_id, session_data)
    
    welcome_message = f"""
🤖 ¡Hola {user.first_name}! Soy **Moody**, tu asistente de orientación psicológica.

🧠 Estoy aquí para ayudarte a explorar tus emociones y brindarte orientación básica a través de:

✅ **Cuestionarios personalizados** según el tipo de terapia
🎤 **Análisis de emociones por voz**
📄 **Reportes detallados en PDF**
💬 **Conversación empática con IA**

Para comenzar, selecciona el tipo de terapia que mejor se adapte a tu situación:
"""
    
    keyboard = []
    for therapy_key, therapy_name in THERAPY_TYPES.items():
        keyboard.append([InlineKeyboardButton(
            f"🔹 {therapy_name}", 
            callback_data=f"therapy_{therapy_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("ℹ️ Ayuda", callback_data="action_help")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help"""
    help_message = """
🤖 **Ayuda - Bot Moody**

**¿Cómo funciona?**
1️⃣ Selecciona un tipo de terapia
2️⃣ Responde 6 preguntas relacionadas
3️⃣ Graba un audio de 10 segundos expresando cómo te sientes
4️⃣ Recibe tu reporte personalizado en PDF
5️⃣ Conversa con nuestra IA empática

**Tipos de terapia disponibles:**
• 👨‍👩‍👧‍👦 **Terapia Familiar** - Para dinámicas familiares
• 💑 **Terapia de Pareja** - Para relaciones de pareja
• 👤 **Terapia Individual** - Para crecimiento personal
• 👩‍🎓 **Terapia para Adolescentes** - Para jóvenes

**Comandos disponibles:**
/start - Iniciar o reiniciar el bot
/help - Mostrar esta ayuda
/resumen - Generar resumen completo de la conversación (solo en chat)

**Nota importante:**
Este bot brinda orientación básica y no reemplaza la consulta con un profesional de la salud mental.

¿Listo para comenzar? Escribe /start
"""
    
    keyboard = [[InlineKeyboardButton("🏠 Volver al inicio", callback_data="action_restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(help_message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode='Markdown')
