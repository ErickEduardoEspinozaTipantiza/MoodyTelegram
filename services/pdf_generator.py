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

async def generate_ai_recommendations(user_session: dict) -> str:
    """Genera recomendaciones usando Ollama/IA"""
    try:
        from services.ollama_client import ollama_client
        
        therapy_type = user_session.get("therapy_name", "No especificado")
        emotion = user_session.get("emotion_detected", "neutral")
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        
        # Resumir respuestas del cuestionario
        answers = user_session.get("answers", [])
        questions = user_session.get("questions", [])
        
        context_summary = ""
        if answers and questions:
            context_summary = "Respuestas clave del cuestionario:\n"
            for i, (q, a) in enumerate(zip(questions[:3], answers[:3]), 1):
                context_summary += f"{i}. {q[:60]}... -> {a[:80]}...\n"
        
        # Crear prompt específico para recomendaciones
        recommendations_prompt = f"""
Como psicólogo clínico especializado, genera un plan de recomendaciones específicas y prácticas para este caso:

PERFIL DEL PACIENTE:
- Tipo de consulta: {therapy_type}
- Estado emocional detectado: {emotion_name}
- Contexto: {context_summary}

Por favor, proporciona RECOMENDACIONES PROFESIONALES ESPECÍFICAS que incluyan:

1. **INTERVENCIONES INMEDIATAS** (esta semana):
   - 3 acciones concretas que puede implementar hoy
   - Técnicas específicas con pasos detallados
   - Horarios y frecuencia recomendada

2. **PLAN A CORTO PLAZO** (próximas 4 semanas):
   - Objetivos terapéuticos medibles
   - Rutinas específicas con cronograma
   - Indicadores de progreso

3. **ESTRATEGIAS DE MANTENIMIENTO** (2-3 meses):
   - Hábitos para sostener el bienestar
   - Red de apoyo recomendada
   - Recursos complementarios

4. **CRITERIOS DE SEGUIMIENTO**:
   - Cuándo buscar ayuda profesional adicional
   - Señales de alarma a monitorear
   - Frecuencia de autoevaluación

Las recomendaciones deben ser:
- Específicas y aplicables inmediatamente
- Basadas en evidencia clínica
- Adaptadas al perfil emocional del usuario
- Con pasos claros y medibles

Responde en formato profesional pero accesible.
"""
        
        # Generar recomendaciones con IA
        ai_recommendations = await ollama_client.generate_response(recommendations_prompt)
        
        if ai_recommendations and len(ai_recommendations.strip()) > 50:
            return ai_recommendations
        else:
            # Fallback a recomendaciones estáticas si Ollama falla
            logger.warning("Ollama no generó recomendaciones válidas, usando fallback")
            return generate_fallback_recommendations(user_session)
            
    except Exception as e:
        logger.error(f"Error generando recomendaciones con IA: {e}")
        return generate_fallback_recommendations(user_session)

def generate_fallback_recommendations(user_session: dict) -> str:
    """Recomendaciones de respaldo cuando Ollama no está disponible"""
    therapy_type = user_session.get("therapy_type", "")
    emotion = user_session.get("emotion_detected", "neutral")
    
    fallback_base = {
        "familiar": """
        **RECOMENDACIONES PARA TERAPIA FAMILIAR**
        
        **Intervenciones inmediatas:**
        • Establecer una reunión familiar semanal de 30 minutos sin dispositivos
        • Implementar la regla de "escuchar sin interrumpir" (2 minutos por persona)
        • Crear un sistema de comunicación positiva diaria
        
        **Plan a corto plazo:**
        • Terapia familiar presencial quincenal durante 3 meses
        • Actividades familiares programadas semanalmente
        • Definir roles y responsabilidades claras por escrito
        """,
        
        "pareja": """
        **RECOMENDACIONES PARA TERAPIA DE PAREJA**
        
        **Intervenciones inmediatas:**
        • Tiempo de calidad diario: 20 minutos sin teléfonos
        • Técnica de validación: repetir lo que entendieron antes de responder
        • Establecer una "cita semanal" sin hablar de problemas
        
        **Plan a corto plazo:**
        • Terapia de pareja cada 15 días durante 2-4 meses
        • Ejercicios de comunicación estructurados
        • Evaluación mensual de objetivos de relación
        """,
        
        "individual": """
        **RECOMENDACIONES PARA TERAPIA INDIVIDUAL**
        
        **Intervenciones inmediatas:**
        • Rutina matutina: despertar a la misma hora + 5 min respiración
        • Journaling: escribir 3 páginas cada mañana
        • Ejercicio físico: 30 min de caminata diaria
        
        **Plan a corto plazo:**
        • Terapia individual semanal durante 6-12 semanas
        • Técnicas de mindfulness 10 min diarios
        • Red de apoyo: contactar 1 persona significativa por semana
        """,
        
        "adolescentes": """
        **RECOMENDACIONES PARA TERAPIA DE ADOLESCENTES**
        
        **Intervenciones inmediatas:**
        • Identificar 2-3 adultos de confianza para conversaciones regulares
        • Técnica 5-4-3-2-1 para momentos de estrés intenso
        • Rutina de sueño consistente (misma hora dormir/despertar)
        
        **Plan a corto plazo:**
        • Terapia para adolescentes cada 10 días durante 3 meses
        • Actividades de descarga emocional: deporte, arte, música
        • Planificación de metas a corto plazo (1 mes)
        """
    }
    
    base_rec = fallback_base.get(therapy_type, "Recomendaciones generales de bienestar emocional.")
    
    # Agregar recomendación específica por emoción
    emotion_additions = {
        "sad": "\n**Para manejo de tristeza:** Aumentar exposición solar 30 min diarios, contacto social 3 veces por semana.",
        "angry": "\n**Para manejo de ira:** Pausa de 10 segundos antes de responder, ejercicio cardiovascular cuando sientas ira.",
        "anxious": "\n**Para manejo de ansiedad:** Respiración 4-7-8, limitar cafeína, técnica de grounding 5-4-3-2-1.",
        "calm": "\n**Mantener calma:** Continuar actividades actuales, crear 'banco de recursos' de relajación.",
        "happy": "\n**Aprovechar estado positivo:** Identificar qué contribuye a tu felicidad, compartir con otros.",
        "fear": "\n**Para manejo de miedo:** Exposición gradual, tener plan B, técnicas de relajación muscular."
    }
    
    return base_rec + emotion_additions.get(emotion, "")

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
        
        # Recomendaciones generadas por IA
        content.append(Paragraph("RECOMENDACIONES PROFESIONALES", heading_style))
        
        recommendations = await generate_ai_recommendations(user_session)
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
    """Genera recomendaciones específicas y prácticas basadas en el tipo de terapia y emoción detectada"""
    therapy_type = user_session.get("therapy_type", "")
    emotion = user_session.get("emotion_detected", "neutral")
    
    base_recommendations = {
        "familiar": """
        <b>Plan de acción para mejorar dinámicas familiares:</b>
        
        • <b>Reuniones familiares semanales:</b> Establezcan una hora fija cada semana (ej: domingos 7pm) para hablar sin dispositivos electrónicos
        • <b>Técnica del "círculo de palabra":</b> Cada miembro tiene 2 minutos para expresarse sin interrupciones
        • <b>Actividad conjunta mensual:</b> Planifiquen una salida o proyecto que involucre a todos
        • <b>Reglas claras de comunicación:</b> Prohibir gritos, usar "yo siento" en lugar de "tú siempre"
        • <b>Roles definidos:</b> Asignar responsabilidades específicas a cada miembro según edad y capacidad
        
        <b>Seguimiento recomendado:</b> Terapia familiar presencial cada 15 días durante 3 meses.
        """,
        
        "pareja": """
        <b>Estrategias específicas para fortalecer la relación:</b>
        
        • <b>Tiempo de calidad diario:</b> 20 minutos sin teléfonos, solo conversación cara a cara
        • <b>Técnica de validación emocional:</b> Antes de responder, repetir lo que entendieron del otro
        • <b>Ritual de conexión semanal:</b> Una cita sin hablar de problemas, solo disfrutar juntos
        • <b>Acuerdos específicos:</b> Definir quién hace qué en casa y cuándo revisar estos acuerdos
        • <b>Ejercicio de gratitud:</b> Cada noche, mencionar una cosa que apreciaron del otro
        
        <b>Seguimiento recomendado:</b> Terapia de pareja quincenal durante 2-4 meses.
        """,
        
        "individual": """
        <b>Plan personalizado de bienestar mental:</b>
        
        • <b>Rutina matutina estructurada:</b> Levantarse a la misma hora, 5 min de respiración profunda, desayuno nutritivo
        • <b>Técnica de journaling:</b> Escribir 3 páginas cada mañana sobre pensamientos y emociones
        • <b>Ejercicio físico dirigido:</b> 30 min de caminata diaria o yoga 3 veces por semana
        • <b>Red de apoyo activa:</b> Contactar a 1 persona significativa cada semana
        • <b>Metas SMART semanales:</b> Objetivos específicos, medibles y alcanzables
        
        <b>Seguimiento recomendado:</b> Terapia individual semanal durante 6-12 semanas.
        """,
        
        "adolescentes": """
        <b>Estrategias adaptadas para desarrollo adolescente:</b>
        
        • <b>Comunicación con adultos de confianza:</b> Identificar 2-3 personas (padres, maestros, familiares) para hablar regularmente
        • <b>Gestión de emociones intensas:</b> Técnica 5-4-3-2-1 (5 cosas que ves, 4 que tocas, 3 que escuchas, etc.)
        • <b>Actividades de descarga emocional:</b> Deporte, arte, música, escritura - elegir 2 que realmente disfrutes
        • <b>Rutina de sueño consistente:</b> Dormir y despertar a la misma hora, sin pantallas 1 hora antes
        • <b>Planificación de futuro:</b> Definir 1 meta a corto plazo (1 mes) y pasos específicos para lograrla
        
        <b>Seguimiento recomendado:</b> Terapia para adolescentes cada 10 días durante 3 meses.
        """
    }
    
    emotion_recommendations = {
        "sad": """
        <b>Protocolo específico para manejo de tristeza:</b>
        - Aumentar exposición a luz solar 30 min diarios
        - Contacto social: llamar a alguien querido 3 veces por semana
        - Actividad física suave: caminar 15 min después de cada comida
        - Evitar aislamiento: salir de casa al menos 1 vez al día""",
        
        "angry": """
        <b>Técnicas de regulación emocional para ira:</b>
        - Pausa de 10 segundos antes de responder en conflictos
        - Ejercicio cardiovascular intenso 20 min cuando sientas ira
        - Técnica de "tiempo fuera": retirarse físicamente de la situación
        - Identificar triggers específicos y crear plan de acción para cada uno""",
        
        "anxious": """
        <b>Protocolo anti-ansiedad estructurado:</b>
        - Respiración 4-7-8: inhalar 4 seg, retener 7, exhalar 8 (repetir 4 veces)
        - Limitar cafeína a 1 taza de café antes del mediodía
        - Técnica de grounding: nombrar 5 objetos del entorno cuando sientas ansiedad
        - Establecer horarios fijos para preocupaciones (ej: 15 min a las 6pm)""",
        
        "calm": """
        <b>Mantener y fortalecer el estado de calma actual:</b>
        - Continuar con las actividades que te generan esta tranquilidad
        - Crear un "banco de recursos": lista de 10 cosas que te relajan
        - Practicar gratitud: escribir 3 cosas positivas cada noche
        - Usar este momento de calma para planificar objetivos importantes""",
        
        "happy": """
        <b>Aprovechar el estado positivo actual:</b>
        - Identificar qué actividades específicas contribuyen a tu felicidad
        - Compartir este estado: planear algo especial con personas importantes
        - Crear "anclas de felicidad": fotos, música, aromas que puedas usar después
        - Usar esta energía para abordar desafíos pendientes""",
        
        "fear": """
        <b>Estrategias graduales para manejo del miedo:</b>
        - Identificar el miedo específico y escribirlo detalladamente
        - Técnica de exposición gradual: enfrentar el miedo en pasos pequeños
        - Red de seguridad: tener plan B y persona de apoyo identificada
        - Técnicas de relajación muscular progresiva antes de situaciones temidas""",
        
        "neutral": """
        <b>Activar y conectar con el bienestar emocional:</b>
        - Explorar nuevas actividades: probar algo diferente cada semana
        - Aumentar consciencia emocional: hacer check-ins contigo mismo 3 veces al día
        - Crear rutinas que generen satisfacción: cocinar, leer, ejercitarse
        - Conectar con otros: iniciar conversaciones más profundas con personas cercanas"""
    }
    
    recommendations = base_recommendations.get(therapy_type, "")
    emotion_rec = emotion_recommendations.get(emotion, "")
    
    if emotion_rec:
        recommendations += f"\n\n{emotion_rec}"
    
    # Agregar indicadores de seguimiento
    recommendations += f"""
    
    <b>Indicadores de progreso a monitorear:</b>
    • Estado de ánimo diario (escala 1-10)
    • Horas de sueño y calidad
    • Nivel de energía y motivación
    • Frecuencia de pensamientos negativos
    • Calidad de relaciones interpersonales
    
    <b>Cuándo buscar ayuda adicional:</b>
    Si después de 2-3 semanas siguiendo estas recomendaciones no observas mejora, 
    o si experimentas pensamientos de autolesión, es crucial buscar apoyo profesional inmediato.
    """
    
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
        
        # Dividir el resumen en párrafos para mejor formato
        if conversation_summary:
            summary_paragraphs = conversation_summary.split('\n\n')
            for paragraph in summary_paragraphs:
                if paragraph.strip():
                    content.append(Paragraph(paragraph.strip(), normal_style))
                    content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("El análisis detallado no pudo ser generado.", normal_style))
        
        content.append(Spacer(1, 20))
        
        # Recomendaciones adicionales generadas por IA
        content.append(Paragraph("RECOMENDACIONES COMPLEMENTARIAS", heading_style))
        
        additional_recommendations = await generate_ai_recommendations(user_session)
        content.append(Paragraph(additional_recommendations, normal_style))
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
