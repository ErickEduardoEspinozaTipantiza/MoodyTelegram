import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from utils.helpers import get_temp_pdf_path, format_user_answers, get_emotion_emoji
from config.settings import EMOTIONS

logger = logging.getLogger(__name__)

async def generate_report_pdf(user_session: dict) -> str:
    """Genera el reporte PDF con los resultados del análisis"""
    try:
        user_id = user_session.get("user_id")
        pdf_path = get_temp_pdf_path(user_id)
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Crear estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Contenido del PDF
        content = []
        
        # Título
        content.append(Paragraph("REPORTE DE ORIENTACIÓN PSICOLÓGICA", title_style))
        content.append(Paragraph("Bot Moody - Análisis Emocional", styles['Heading3']))
        content.append(Spacer(1, 20))
        
        # Información del usuario
        user_info = f"""
        <b>Fecha del análisis:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}<br/>
        <b>Usuario:</b> {user_session.get('first_name', 'Usuario')}<br/>
        <b>Tipo de terapia:</b> {user_session.get('therapy_name', 'No especificado')}
        """
        content.append(Paragraph(user_info, normal_style))
        content.append(Spacer(1, 20))
        
        # Respuestas del cuestionario
        content.append(Paragraph("RESPUESTAS DEL CUESTIONARIO", heading_style))
        
        questions = user_session.get("questions", [])
        answers = user_session.get("answers", [])
        
        if questions and answers:
            for i, (question, answer) in enumerate(zip(questions, answers), 1):
                content.append(Paragraph(f"<b>Pregunta {i}:</b> {question}", normal_style))
                content.append(Paragraph(f"<b>Respuesta:</b> {answer}", normal_style))
                content.append(Spacer(1, 10))
        
        content.append(Spacer(1, 20))
        
        # Análisis emocional
        content.append(Paragraph("ANÁLISIS EMOCIONAL POR VOZ", heading_style))
        
        emotion = user_session.get("emotion_detected", "neutral")
        confidence = user_session.get("emotion_confidence", 0.0)
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        
        emotion_analysis = f"""
        <b>Emoción detectada:</b> {emotion_name}<br/>
        <b>Nivel de confianza:</b> {confidence*100:.1f}%<br/>
        <b>Descripción:</b> {user_session.get('emotion_description', 'No disponible')}
        """
        content.append(Paragraph(emotion_analysis, normal_style))
        content.append(Spacer(1, 20))
        
        # Recomendaciones
        content.append(Paragraph("RECOMENDACIONES GENERALES", heading_style))
        
        recommendations = generate_recommendations(user_session)
        content.append(Paragraph(recommendations, normal_style))
        content.append(Spacer(1, 20))
        
        # Contacto de especialista
        content.append(Paragraph("CONTACTO DE ESPECIALISTA", heading_style))
        
        specialist_info = """
        Para un seguimiento profesional más detallado, te recomendamos contactar con:
        
        <b>Centro de Salud Mental</b><br/>
        Email: crisgeopro2003@gmail.com<br/>
        Teléfono: +1 (555) 123-4567<br/>
        
        <i>Nota: Este reporte es una orientación básica y no reemplaza la consulta con un profesional de la salud mental.</i>
        """
        content.append(Paragraph(specialist_info, normal_style))
        
        # Construir el PDF
        doc.build(content)
        
        logger.info(f"PDF generado exitosamente: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return None

def generate_recommendations(user_session: dict) -> str:
    """Genera recomendaciones basadas en el tipo de terapia y emoción detectada"""
    therapy_type = user_session.get("therapy_type", "")
    emotion = user_session.get("emotion_detected", "neutral")
    
    base_recommendations = {
        "familiar": """
        Para mejorar las dinámicas familiares, considera:
        • Establecer momentos regulares de comunicación familiar
        • Practicar la escucha activa con cada miembro
        • Definir roles y responsabilidades claras
        • Buscar actividades que unan a la familia
        """,
        
        "pareja": """
        Para fortalecer tu relación de pareja, te sugerimos:
        • Dedicar tiempo de calidad juntos sin distracciones
        • Practicar la comunicación asertiva y empática
        • Trabajar en la resolución constructiva de conflictos
        • Mantener la intimidad emocional y física
        """,
        
        "individual": """
        Para tu crecimiento personal, considera:
        • Practicar técnicas de mindfulness y meditación
        • Establecer metas personales realistas y alcanzables
        • Desarrollar hábitos saludables de autocuidado
        • Buscar actividades que te generen satisfacción
        """,
        
        "adolescentes": """
        Para navegar mejor esta etapa de tu vida:
        • Mantén una comunicación abierta con adultos de confianza
        • Desarrolla estrategias saludables para manejar el estrés
        • Explora tus intereses y talentos
        • Construye relaciones positivas con tus pares
        """
    }
    
    emotion_recommendations = {
        "sad": "Es importante expresar tus sentimientos y buscar apoyo social.",
        "angry": "Practica técnicas de relajación y manejo de la ira.",
        "anxious": "Considera técnicas de respiración y relajación progresiva.",
        "calm": "Mantén este estado positivo con prácticas de bienestar.",
        "happy": "Aprovecha este estado para trabajar en tus objetivos.",
        "fear": "Identifica las fuentes de tu miedo y busca estrategias de afrontamiento.",
        "neutral": "Explora actividades que te ayuden a conectar con tus emociones."
    }
    
    recommendations = base_recommendations.get(therapy_type, "")
    emotion_rec = emotion_recommendations.get(emotion, "")
    
    if emotion_rec:
        recommendations += f"\n\n<b>Considerando tu estado emocional actual:</b> {emotion_rec}"
    
    return recommendations

async def generate_conversation_summary_pdf(user_session: dict, conversation_summary: str) -> str:
    """Genera un PDF con el resumen completo de la conversación"""
    try:
        user_id = user_session.get("user_id")
        pdf_path = get_temp_pdf_path(f"{user_id}_resumen")
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Obtener estilos
        styles = getSampleStyleSheet()
        
        # Crear estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Contenido del PDF
        content = []
        
        # Título
        content.append(Paragraph("RESUMEN COMPLETO DE SESIÓN", title_style))
        content.append(Paragraph("Bot Moody - Análisis y Conversación", styles['Heading3']))
        content.append(Spacer(1, 20))
        
        # Información del usuario
        user_info = f"""
        <b>Fecha de la sesión:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}<br/>
        <b>Usuario:</b> {user_session.get('first_name', 'Usuario')}<br/>
        <b>Tipo de terapia:</b> {user_session.get('therapy_name', 'No especificado')}<br/>
        <b>Duración de conversación:</b> {len(user_session.get('chat_history', []))} intercambios
        """
        content.append(Paragraph(user_info, normal_style))
        content.append(Spacer(1, 20))
        
        # Análisis inicial
        content.append(Paragraph("ANÁLISIS INICIAL", heading_style))
        
        # Respuestas del cuestionario (resumidas)
        questions = user_session.get("questions", [])
        answers = user_session.get("answers", [])
        
        if questions and answers:
            content.append(Paragraph("<b>Cuestionario completado:</b>", normal_style))
            for i, (question, answer) in enumerate(zip(questions[:3], answers[:3]), 1):  # Solo primeras 3
                content.append(Paragraph(f"<b>{i}.</b> {question[:80]}{'...' if len(question) > 80 else ''}", normal_style))
                content.append(Paragraph(f"<i>Respuesta:</i> {answer[:100]}{'...' if len(answer) > 100 else ''}", normal_style))
                content.append(Spacer(1, 8))
            
            if len(questions) > 3:
                content.append(Paragraph(f"<i>[Y {len(questions)-3} preguntas adicionales...]</i>", normal_style))
        
        content.append(Spacer(1, 15))
        
        # Análisis emocional
        emotion = user_session.get("emotion_detected", "neutral")
        confidence = user_session.get("emotion_confidence", 0.0)
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        
        emotion_analysis = f"""
        <b>Emoción detectada por voz:</b> {emotion_name}<br/>
        <b>Nivel de confianza:</b> {confidence*100:.1f}%<br/>
        """
        content.append(Paragraph(emotion_analysis, normal_style))
        content.append(Spacer(1, 20))
        
        # Historial de conversación (resumido)
        content.append(Paragraph("PUNTOS CLAVE DE LA CONVERSACIÓN", heading_style))
        
        chat_history = user_session.get("chat_history", [])
        if chat_history:
            content.append(Paragraph(f"<b>Total de intercambios:</b> {len(chat_history)}", normal_style))
            
            # Mostrar algunos intercambios clave
            key_exchanges = chat_history[:2] + chat_history[-2:] if len(chat_history) > 4 else chat_history
            
            for i, exchange in enumerate(key_exchanges, 1):
                user_msg = exchange['user'][:150] + ('...' if len(exchange['user']) > 150 else '')
                bot_msg = exchange['bot'][:200] + ('...' if len(exchange['bot']) > 200 else '')
                
                content.append(Paragraph(f"<b>Intercambio {i}:</b>", normal_style))
                content.append(Paragraph(f"<i>Usuario:</i> {user_msg}", normal_style))
                content.append(Paragraph(f"<i>Respuesta:</i> {bot_msg}", normal_style))
                content.append(Spacer(1, 10))
        
        content.append(Spacer(1, 20))
        
        # Resumen profesional generado por IA
        content.append(Paragraph("ANÁLISIS PROFESIONAL COMPLETO", heading_style))
        
        # Dividir el resumen en párrafos
        summary_paragraphs = conversation_summary.split('\n\n')
        for paragraph in summary_paragraphs:
            if paragraph.strip():
                content.append(Paragraph(paragraph.strip(), normal_style))
                content.append(Spacer(1, 10))
        
        content.append(Spacer(1, 20))
        
        # Información de contacto
        content.append(Paragraph("INFORMACIÓN DE CONTACTO", heading_style))
        
        contact_info = """
        <b>Para seguimiento profesional:</b><br/>
        Email: crisgeopro2003@gmail.com<br/>
        
        <i>Nota: Este resumen es generado por IA y tiene propósitos informativos. 
        No reemplaza la consulta con un profesional de la salud mental.</i>
        """
        content.append(Paragraph(contact_info, normal_style))
        
        # Construir el PDF
        doc.build(content)
        
        logger.info(f"PDF de resumen generado exitosamente: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generando PDF de resumen: {e}")
        return None

def get_temp_pdf_path(filename: str) -> str:
    """Genera la ruta del archivo PDF temporal con nombre personalizado"""
    from utils.helpers import TEMP_PATH
    return os.path.join(TEMP_PATH, f"{filename}.pdf")
