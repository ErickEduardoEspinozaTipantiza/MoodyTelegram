import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config.settings import EMAIL_USER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

logger = logging.getLogger(__name__)

async def send_email_with_pdf(pdf_path: str, user_id: int, is_summary: bool = False) -> bool:
    """Envía el PDF por email"""
    try:
        # Verificar configuración de email
        if not validate_email_config():
            logger.warning("Configuración de email incompleta, saltando envío")
            return False
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            logger.error(f"Archivo PDF no encontrado: {pdf_path}")
            return False
        
        # Configurar el mensaje
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = "crisgeopro2003@gmail.com"
        
        if is_summary:
            msg['Subject'] = f"Resumen Completo de Conversación - Usuario {user_id}"
            filename = f"resumen_completo_moody_{user_id}.pdf"
            body = f"""
Estimado equipo,

Se adjunta el resumen completo de la conversación con análisis profesional generado por el Bot Moody.

Detalles del resumen:
- Usuario ID: {user_id}
- Fecha de generación: {os.path.getctime(pdf_path)}
- Archivo: {filename}

Este resumen incluye:
• Análisis emocional inicial
• Historial completo de conversación
• Insights y patrones identificados por IA
• Recomendaciones profesionales específicas
• Próximos pasos sugeridos

Por favor, revisar para seguimiento profesional.

Saludos,
Bot Moody - Sistema de Orientación Psicológica
            """
        else:
            msg['Subject'] = f"Reporte de Orientación Psicológica - Usuario {user_id}"
            filename = f"reporte_moody_{user_id}.pdf"
            body = f"""
Estimado equipo,

Se adjunta el reporte de orientación psicológica generado por el Bot Moody.

Detalles del reporte:
- Usuario ID: {user_id}
- Fecha de generación: {os.path.getctime(pdf_path)}
- Archivo: {filename}

Este reporte contiene:
• Respuestas del cuestionario de terapia
• Análisis de emociones por voz
• Recomendaciones personalizadas

Por favor, revisar y dar seguimiento según corresponda.

Saludos,
Bot Moody - Sistema de Orientación Psicológica
            """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Adjuntar el PDF
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        msg.attach(part)
        
        # Enviar el email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        # Solo intentar login si tenemos credenciales
        if EMAIL_PASSWORD:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        server.sendmail(EMAIL_USER, "crisgeopro2003@gmail.com", msg.as_string())
        server.quit()
        
        logger.info(f"Email enviado exitosamente para el usuario {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email para usuario {user_id}: {e}")
        return False

def validate_email_config() -> bool:
    """Valida que la configuración de email esté correcta"""
    if not EMAIL_USER:
        logger.warning("EMAIL_USER no configurado")
        return False
    
    if not EMAIL_PASSWORD:
        logger.warning("EMAIL_PASSWORD no configurado")
        return False
    
    return True
