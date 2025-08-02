import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config.settings import TELEGRAM_BOT_TOKEN, BotStates
from handlers.start_handler import start_command, help_command
from handlers.therapy_handler import handle_therapy_selection, handle_question_answer
from handlers.voice_handler import handle_voice_message
from handlers.chat_handler import handle_chat_message
from utils.helpers import create_temp_directory, load_user_session, save_user_session

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MoodyBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Configura todos los handlers del bot"""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        
        # Callback handlers para botones inline
        self.application.add_handler(CallbackQueryHandler(handle_therapy_selection, pattern="^therapy_"))
        self.application.add_handler(CallbackQueryHandler(self.handle_action_buttons, pattern="^action_"))
        
        # Handlers de mensajes
        self.application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.route_text_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def route_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ruta los mensajes de texto según el estado actual del usuario"""
        user_id = update.effective_user.id
        user_session = load_user_session(user_id)
        
        state = user_session.get("state", BotStates.START)
        
        if state == BotStates.ANSWERING_QUESTIONS:
            await handle_question_answer(update, context)
        elif state == BotStates.CHAT_WITH_LLM:
            await handle_chat_message(update, context)
        else:
            await update.message.reply_text(
                "Por favor, usa los botones del menú o escribe /start para comenzar."
            )
    
    async def handle_action_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja los botones de acción como enviar email, descargar PDF, etc."""
        query = update.callback_query
        await query.answer()
        
        action = query.data.replace("action_", "")
        user_id = update.effective_user.id
        
        if action == "send_email":
            await self.send_email_action(update, context)
        elif action == "download_pdf":
            await self.download_pdf_action(update, context)
        elif action == "chat_llm":
            await self.start_chat_action(update, context)
        elif action == "generate_summary":
            await self.generate_summary_action(update, context)
        elif action == "send_summary_email":
            await self.send_summary_email_action(update, context)
        elif action == "download_summary":
            await self.download_summary_action(update, context)
        elif action == "continue_chat":
            await self.continue_chat_action(update, context)
        elif action == "restart":
            await start_command(update, context)
    
    async def send_email_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Envía el PDF por email"""
        try:
            from services.email_service import send_email_with_pdf
            
            user_id = update.effective_user.id
            user_session = load_user_session(user_id)
            
            if "pdf_path" in user_session:
                success = await send_email_with_pdf(user_session["pdf_path"], user_id)
                if success:
                    message = "✅ Reporte enviado exitosamente a crisgeopro2003@gmail.com"
                else:
                    message = "❌ Error al enviar el email. Intenta más tarde."
            else:
                message = "❌ No se encontró el reporte para enviar."
                
            await update.callback_query.edit_message_text(message)
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error interno al enviar el email."
            )
    
    async def download_pdf_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Permite descargar el PDF"""
        user_id = update.effective_user.id
        user_session = load_user_session(user_id)
        
        if "pdf_path" in user_session and os.path.exists(user_session["pdf_path"]):
            with open(user_session["pdf_path"], 'rb') as pdf_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=pdf_file,
                    filename=f"reporte_moody_{user_id}.pdf",
                    caption="📄 Aquí tienes tu reporte de orientación psicológica"
                )
        else:
            await update.callback_query.edit_message_text(
                "❌ No se pudo encontrar el archivo PDF."
            )
    
    async def start_chat_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el chat con LLM"""
        user_id = update.effective_user.id
        user_session = load_user_session(user_id)
        user_session["state"] = BotStates.CHAT_WITH_LLM
        save_user_session(user_id, user_session)
        
        await update.callback_query.edit_message_text(
            "🤖 Ahora puedes conversar conmigo sobre tus emociones. "
            "Estoy aquí para escucharte y ayudarte.\n\n"
            "Escribe cualquier mensaje para comenzar nuestra conversación. "
            "Puedes escribir /start en cualquier momento para volver al menú principal.\n\n"
            "💡 **Tip:** Escribe '/resumen' cuando quieras que genere un análisis completo de nuestra conversación."
        )
    
    async def generate_summary_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Genera resumen de la conversación actual"""
        from handlers.chat_handler import generate_conversation_summary
        await generate_conversation_summary(update, context)
    
    async def send_summary_email_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Envía el resumen por email"""
        try:
            from services.email_service import send_email_with_pdf
            
            user_id = update.effective_user.id
            user_session = load_user_session(user_id)
            
            summary_pdf_path = user_session.get("summary_pdf_path")
            if summary_pdf_path and os.path.exists(summary_pdf_path):
                success = await send_email_with_pdf(summary_pdf_path, user_id, is_summary=True)
                if success:
                    message = "✅ Resumen completo enviado exitosamente a crisgeopro2003@gmail.com"
                else:
                    message = "❌ Error al enviar el email del resumen. Intenta más tarde."
            else:
                message = "❌ No se encontró el resumen para enviar."
                
            await update.callback_query.edit_message_text(message)
            
        except Exception as e:
            logger.error(f"Error enviando resumen por email: {e}")
            await update.callback_query.edit_message_text(
                "❌ Error interno al enviar el resumen por email."
            )
    
    async def download_summary_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Permite descargar el resumen en PDF"""
        user_id = update.effective_user.id
        user_session = load_user_session(user_id)
        
        summary_pdf_path = user_session.get("summary_pdf_path")
        if summary_pdf_path and os.path.exists(summary_pdf_path):
            with open(summary_pdf_path, 'rb') as pdf_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=pdf_file,
                    filename=f"resumen_completo_moody_{user_id}.pdf",
                    caption="📋 Aquí tienes tu resumen completo de la sesión con análisis profesional"
                )
        else:
            await update.callback_query.edit_message_text(
                "❌ No se pudo encontrar el archivo de resumen."
            )
    
    async def continue_chat_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Continúa la conversación después del resumen"""
        await update.callback_query.edit_message_text(
            "💬 **Conversación continúa**\n\n"
            "Puedes seguir hablando conmigo sobre cualquier tema relacionado con tus emociones.\n\n"
            "Escribe '/resumen' en cualquier momento para generar un nuevo análisis actualizado."
        )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja errores del bot"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error inesperado. Por favor, intenta nuevamente o escribe /start."
            )
    
    def run(self):
        """Inicia el bot"""
        # Crear directorios necesarios
        create_temp_directory()
        
        logger.info("🤖 Bot Moody iniciado...")
        print("🤖 Bot Moody iniciado y listo para recibir mensajes!")
        
        # Ejecutar el bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = MoodyBot()
    bot.run()
