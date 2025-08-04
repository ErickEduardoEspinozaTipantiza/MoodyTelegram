import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.tableofcontents import TableOfContents
from utils.helpers import get_temp_pdf_path, format_user_answers, get_emotion_emoji
from config.settings import EMOTIONS

logger = logging.getLogger(__name__)

def create_header_with_logo():
    """Crea el encabezado profesional con logo"""
    try:
        # Ruta del logo
        logo_path = os.path.join(os.path.dirname(__file__), "Mody.jpg")
        
        if os.path.exists(logo_path):
            # Crear tabla para el encabezado
            header_data = [
                [
                    Image(logo_path, width=2*inch, height=1.5*inch),
                    [
                        Paragraph("<font size=20><b>MOODY BOT</b></font>", 
                                ParagraphStyle('HeaderTitle', fontSize=20, textColor=colors.darkblue, alignment=TA_CENTER)),
                        Paragraph("<font size=12>Análisis Psicológico Inteligente</font>", 
                                ParagraphStyle('HeaderSubtitle', fontSize=12, textColor=colors.grey, alignment=TA_CENTER)),
                        Paragraph("<font size=10>Reporte Profesional de Orientación</font>", 
                                ParagraphStyle('HeaderDesc', fontSize=10, textColor=colors.darkgrey, alignment=TA_CENTER))
                    ]
                ]
            ]
            
            header_table = Table(header_data, colWidths=[2.5*inch, 4*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            return header_table
        else:
            # Encabezado sin logo si no se encuentra la imagen
            return Paragraph("<font size=20><b>MOODY BOT</b></font><br/><font size=12>Análisis Psicológico Inteligente</font>", 
                           ParagraphStyle('HeaderNoLogo', fontSize=20, textColor=colors.darkblue, alignment=TA_CENTER))
    except Exception as e:
        logger.warning(f"Error creando encabezado con logo: {e}")
        return Paragraph("<font size=20><b>MOODY BOT</b></font><br/><font size=12>Análisis Psicológico Inteligente</font>", 
                       ParagraphStyle('HeaderNoLogo', fontSize=20, textColor=colors.darkblue, alignment=TA_CENTER))

def create_professional_styles():
    """Crea estilos profesionales personalizados"""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        'title': ParagraphStyle(
            'ProfessionalTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        ),
        
        'subtitle': ParagraphStyle(
            'ProfessionalSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2e5984'),
            fontName='Helvetica-Bold'
        ),
        
        'section_header': ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#0066cc'),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#0066cc'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f8ff')
        ),
        
        'subsection_header': ParagraphStyle(
            'SubsectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.HexColor('#004080'),
            fontName='Helvetica-Bold'
        ),
        
        'body_text': ParagraphStyle(
            'ProfessionalBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        ),
        
        'highlight_box': ParagraphStyle(
            'HighlightBox',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            spaceBefore=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            backColor=colors.HexColor('#f8f9fa'),
            borderWidth=1,
            borderColor=colors.HexColor('#dee2e6'),
            borderPadding=10,
            leftIndent=10,
            rightIndent=10
        ),
        
        'footer_text': ParagraphStyle(
            'FooterText',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='Helvetica-Oblique'
        )
    }
    
    return custom_styles

def create_info_table(user_session: dict):
    """Crea una tabla profesional con información del usuario"""
    data = [
        ['Fecha del Análisis:', datetime.now().strftime("%d de %B de %Y, %H:%M hrs")],
        ['Usuario:', user_session.get('first_name', 'Usuario')],
        ['Tipo de Terapia:', user_session.get('therapy_name', 'No especificado')],
        ['ID de Sesión:', str(user_session.get('user_id', 'N/A'))],
        ['Estado de la Evaluación:', 'Completada']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 3.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4fd')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    return table

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
        
        # Crear prompt más específico y detallado para recomendaciones profesionales
        recommendations_prompt = f"""
ERES UN PSICÓLOGO CLÍNICO ESPECIALIZADO. Genera ÚNICAMENTE recomendaciones profesionales específicas, NO conversación.

DATOS DEL CASO:
- Tipo de terapia: {therapy_type}
- Emoción predominante: {emotion_name}
- Respuestas del cuestionario: {context_summary}

INSTRUCCIONES ESTRICTAS:
- NO hagas preguntas al paciente
- NO uses lenguaje conversacional como "¿Te gustaría...?" o "A veces..."
- SOLO proporciona recomendaciones directas y profesionales
- Usa formato de lista con viñetas
- Sé específico y práctico

GENERA EXCLUSIVAMENTE:

**RECOMENDACIONES INMEDIATAS (próximos 7 días):**
• [Técnica específica 1 con pasos concretos]
• [Técnica específica 2 con frecuencia]
• [Acción práctica 3 con horario]

**PLAN A MEDIANO PLAZO (4 semanas):**
• [Estrategia 1 con cronograma]
• [Hábito 2 con indicadores medibles]
• [Objetivo 3 con seguimiento]

**ESTRATEGIAS DE MANTENIMIENTO:**
• [Herramienta 1 para automonitoreo]
• [Red de apoyo específica]
• [Recursos complementarios]

**CRITERIOS DE DERIVACIÓN:**
• Buscar ayuda profesional si [criterio específico]
• Contactar especialista cuando [situación específica]

Responde SOLO con las recomendaciones en formato de lista, sin introducción ni despedida.
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
    """Genera el reporte PDF profesional con los resultados del análisis"""
    try:
        user_id = user_session.get("user_id")
        pdf_path = get_temp_pdf_path(user_id)
        
        # Crear el documento PDF con márgenes profesionales
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Obtener estilos profesionales
        styles = create_professional_styles()
        
        # Contenido del PDF
        content = []
        
        # Encabezado con logo
        header = create_header_with_logo()
        content.append(header)
        content.append(Spacer(1, 30))
        
        # Línea separadora
        line_table = Table([['']], colWidths=[6*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#0066cc')),
        ]))
        content.append(line_table)
        content.append(Spacer(1, 20))
        
        # Título principal
        content.append(Paragraph("REPORTE DE ORIENTACIÓN PSICOLÓGICA", styles['title']))
        content.append(Spacer(1, 10))
        
        # Información del usuario en tabla profesional
        content.append(Paragraph("INFORMACIÓN DE LA SESIÓN", styles['section_header']))
        content.append(Spacer(1, 10))
        user_table = create_info_table(user_session)
        content.append(user_table)
        content.append(Spacer(1, 25))
        
        # Cuestionario de evaluación
        content.append(Paragraph("EVALUACIÓN INICIAL", styles['section_header']))
        content.append(Spacer(1, 10))
        
        questions = user_session.get("questions", [])
        answers = user_session.get("answers", [])
        
        if questions and answers:
            # Crear estilos para las celdas de la tabla
            header_style = ParagraphStyle(
                'TableHeader',
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=colors.white,
                alignment=TA_CENTER
            )
            
            cell_style = ParagraphStyle(
                'TableCell',
                fontSize=9,
                fontName='Helvetica',
                alignment=TA_LEFT,
                leading=12
            )
            
            # Crear los datos de la tabla con Paragraphs para ajuste automático
            qa_data = [
                [Paragraph('Pregunta', header_style), Paragraph('Respuesta', header_style)]
            ]
            
            for i, (question, answer) in enumerate(zip(questions, answers), 1):
                # Crear párrafos que se ajusten automáticamente al ancho de la celda
                question_paragraph = Paragraph(f"<b>{i}.</b> {question}", cell_style)
                answer_paragraph = Paragraph(answer, cell_style)
                qa_data.append([question_paragraph, answer_paragraph])
            
            # Ajustar anchos de columnas: pregunta un poco más ancha que respuesta
            qa_table = Table(qa_data, colWidths=[2.8*inch, 3.2*inch])
            qa_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            content.append(qa_table)
        else:
            content.append(Paragraph("No se completó el cuestionario de evaluación.", styles['body_text']))
        
        content.append(Spacer(1, 25))
        
        # Análisis emocional con diseño destacado
        content.append(Paragraph("ANÁLISIS EMOCIONAL POR VOZ", styles['section_header']))
        content.append(Spacer(1, 10))
        
        emotion = user_session.get("emotion_detected", "neutral")
        confidence = user_session.get("emotion_confidence", 0.0)
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        emotion_emoji = get_emotion_emoji(emotion)
        
        # Crear tabla para análisis emocional
        emotion_data = [
            ['Parámetro', 'Resultado'],
            ['Emoción Detectada', f"{emotion_emoji} {emotion_name}"],
            ['Nivel de Confianza', f"{confidence*100:.1f}%"],
            ['Descripción', user_session.get('emotion_description', 'Análisis completado exitosamente')]
        ]
        
        emotion_table = Table(emotion_data, colWidths=[2.5*inch, 3.5*inch])
        emotion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(emotion_table)
        content.append(Spacer(1, 25))
        
        # Especialista asignado con información completa
        content.append(Paragraph("ESPECIALISTA ASIGNADO", styles['section_header']))
        content.append(Spacer(1, 10))
        
        # Obtener especialista según tipo de terapia
        from config.settings import SPECIALISTS
        therapy_type = user_session.get("therapy_type", "individual")
        specialist = SPECIALISTS.get(therapy_type, SPECIALISTS["individual"])
        
        # Crear tabla profesional para información del especialista
        specialist_data = [
            ['Especialista', specialist['name']],
            ['Título', specialist['title']],
            ['Credenciales', specialist['credentials']],
            ['Experiencia', specialist['experience']],
            ['Especialidades', ', '.join(specialist['specialties'])],
            ['Email', specialist['email']],
            ['Teléfono', specialist['phone']]
        ]
        
        specialist_table = Table(specialist_data, colWidths=[2*inch, 4*inch])
        specialist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#17a2b8')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#e8f4fd'), colors.white]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(specialist_table)
        content.append(Spacer(1, 20))
        
        # Nota profesional
        note_text = """
        <b>NOTA IMPORTANTE:</b> Este reporte ha sido generado por un sistema de inteligencia artificial 
        como herramienta de orientación inicial. Los resultados aquí presentados tienen fines informativos 
        y educativos, y <b>NO sustituyen</b> la evaluación, diagnóstico o tratamiento de un profesional 
        de la salud mental cualificado.
        
        Se recomienda encarecidamente consultar con el especialista asignado para una evaluación 
        profesional completa y personalizada. Las recomendaciones específicas de tratamiento serán 
        proporcionadas directamente por el especialista a través de los canales apropiados.
        """
        content.append(Paragraph(note_text, styles['highlight_box']))
        
        # Footer con información adicional
        content.append(Spacer(1, 30))
        footer_text = f"""
        Reporte generado por Moody Bot - Sistema de Análisis Psicológico Inteligente
        Fecha: {datetime.now().strftime("%d de %B de %Y a las %H:%M hrs")}
        Versión del sistema: 2.0 | ID de sesión: {user_session.get('user_id', 'N/A')}
        """
        content.append(Paragraph(footer_text, styles['footer_text']))
        
        # Construir el PDF
        doc.build(content)
        
        logger.info(f"PDF profesional generado exitosamente: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generando PDF profesional: {e}")
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
    """Genera un PDF profesional con el resumen completo de la conversación"""
    try:
        user_id = user_session.get("user_id")
        pdf_path = get_temp_pdf_path(f"{user_id}_resumen")
        
        # Crear el documento PDF con diseño profesional
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Obtener estilos profesionales
        styles = create_professional_styles()
        
        # Contenido del PDF
        content = []
        
        # Encabezado con logo
        header = create_header_with_logo()
        content.append(header)
        content.append(Spacer(1, 30))
        
        # Línea separadora
        line_table = Table([['']], colWidths=[6*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#0066cc')),
        ]))
        content.append(line_table)
        content.append(Spacer(1, 20))
        
        # Título principal
        content.append(Paragraph("RESUMEN COMPLETO DE SESIÓN TERAPÉUTICA", styles['title']))
        content.append(Spacer(1, 10))
        
        # Información de la sesión
        content.append(Paragraph("DATOS DE LA SESIÓN", styles['section_header']))
        content.append(Spacer(1, 10))
        
        session_data = [
            ['Fecha de la Sesión:', datetime.now().strftime("%d de %B de %Y, %H:%M hrs")],
            ['Usuario:', user_session.get('first_name', 'Usuario')],
            ['Tipo de Terapia:', user_session.get('therapy_name', 'No especificado')],
            ['Duración de Conversación:', f"{len(user_session.get('chat_history', []))} intercambios"],
            ['Estado de la Evaluación:', 'Completada con análisis IA'],
            ['Nivel de Detalle:', 'Resumen Profesional Completo']
        ]
        
        session_table = Table(session_data, colWidths=[2.5*inch, 3.5*inch])
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4fd')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(session_table)
        content.append(Spacer(1, 25))
        
        # Evaluación inicial resumida
        content.append(Paragraph("EVALUACIÓN INICIAL", styles['section_header']))
        content.append(Spacer(1, 10))
        
        questions = user_session.get("questions", [])
        answers = user_session.get("answers", [])
        
        if questions and answers:
            content.append(Paragraph("<b>Resumen del Cuestionario Completado:</b>", styles['subsection_header']))
            content.append(Spacer(1, 5))
            
            # Mostrar solo las primeras 3 preguntas/respuestas más importantes
            for i, (question, answer) in enumerate(zip(questions[:3], answers[:3]), 1):
                q_text = question if len(question) <= 100 else question[:97] + "..."
                a_text = answer if len(answer) <= 120 else answer[:117] + "..."
                
                qa_text = f"<b>{i}.</b> {q_text}<br/><i>Respuesta:</i> {a_text}"
                content.append(Paragraph(qa_text, styles['body_text']))
                content.append(Spacer(1, 8))
            
            if len(questions) > 3:
                content.append(Paragraph(f"<i>[Y {len(questions)-3} preguntas adicionales completadas...]</i>", 
                                       styles['body_text']))
        else:
            content.append(Paragraph("No se completó cuestionario de evaluación inicial.", styles['body_text']))
        
        content.append(Spacer(1, 20))
        
        # Análisis emocional
        content.append(Paragraph("ANÁLISIS EMOCIONAL", styles['section_header']))
        content.append(Spacer(1, 10))
        
        emotion = user_session.get("emotion_detected", "neutral")
        confidence = user_session.get("emotion_confidence", 0.0)
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        emotion_emoji = get_emotion_emoji(emotion)
        
        emotion_summary = f"""
        <b>Estado Emocional Detectado:</b> {emotion_emoji} {emotion_name}<br/>
        <b>Confiabilidad del Análisis:</b> {confidence*100:.1f}%<br/>
        <b>Método de Análisis:</b> Procesamiento de audio por IA<br/>
        <b>Resultado:</b> Análisis completado exitosamente
        """
        content.append(Paragraph(emotion_summary, styles['highlight_box']))
        content.append(Spacer(1, 20))
        
        # Puntos clave de la conversación
        content.append(Paragraph("ASPECTOS DESTACADOS DE LA CONVERSACIÓN", styles['section_header']))
        content.append(Spacer(1, 10))
        
        chat_history = user_session.get("chat_history", [])
        if chat_history:
            content.append(Paragraph(f"<b>Total de intercambios registrados:</b> {len(chat_history)}", 
                                   styles['subsection_header']))
            content.append(Spacer(1, 10))
            
            # Mostrar intercambios más relevantes
            key_exchanges = chat_history[:2] + chat_history[-2:] if len(chat_history) > 4 else chat_history
            
            # Estilo para el contenido de las tablas de intercambios
            exchange_label_style = ParagraphStyle(
                'ExchangeLabel',
                fontSize=9,
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT
            )
            
            exchange_content_style = ParagraphStyle(
                'ExchangeContent',
                fontSize=9,
                fontName='Helvetica',
                alignment=TA_LEFT,
                leading=11
            )
            
            for i, exchange in enumerate(key_exchanges, 1):
                # Usar los mensajes completos sin truncar, el Paragraph se encargará del ajuste
                user_msg = exchange['user']
                bot_msg = exchange['bot']
                
                exchange_data = [
                    [Paragraph('Usuario:', exchange_label_style), 
                     Paragraph(user_msg, exchange_content_style)],
                    [Paragraph('Respuesta del Sistema:', exchange_label_style), 
                     Paragraph(bot_msg, exchange_content_style)]
                ]
                
                exchange_table = Table(exchange_data, colWidths=[1.8*inch, 4.2*inch])
                exchange_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                content.append(exchange_table)
                content.append(Spacer(1, 15))
                
            if len(chat_history) > 4:
                content.append(Paragraph(f"<i>[{len(chat_history)-4} intercambios adicionales en la conversación...]</i>", 
                                       styles['body_text']))
        else:
            content.append(Paragraph("No se registraron intercambios en la conversación.", styles['body_text']))
        
        content.append(Spacer(1, 25))
        
        # Análisis profesional completo por IA
        content.append(Paragraph("ANÁLISIS PROFESIONAL INTEGRAL", styles['section_header']))
        content.append(Spacer(1, 10))
        
        if conversation_summary and conversation_summary.strip():
            # Dividir el resumen en secciones para mejor formato
            summary_sections = conversation_summary.split('\n\n')
            for section in summary_sections:
                if section.strip():
                    content.append(Paragraph(section.strip(), styles['body_text']))
                    content.append(Spacer(1, 10))
        else:
            fallback_summary = """
            <b>Resumen Automático:</b><br/>
            Durante esta sesión, el usuario completó una evaluación integral que incluyó tanto un cuestionario 
            estructurado como análisis emocional por voz. Los resultados proporcionan una base sólida para 
            recomendaciones de seguimiento y orientación terapéutica personalizada.
            
            El análisis indica la necesidad de seguimiento profesional según el tipo de terapia identificado 
            y las características emocionales detectadas.
            """
            content.append(Paragraph(fallback_summary, styles['highlight_box']))
        
        content.append(Spacer(1, 25))
        
        # Especialista para seguimiento
        content.append(Paragraph("PROFESIONAL ASIGNADO PARA SEGUIMIENTO", styles['section_header']))
        content.append(Spacer(1, 10))
        
        from config.settings import SPECIALISTS
        therapy_type = user_session.get("therapy_type", "individual")
        specialist = SPECIALISTS.get(therapy_type, SPECIALISTS["individual"])
        
        # Información del especialista en formato profesional
        specialist_data = [
            ['Profesional Asignado', specialist['name']],
            ['Título Profesional', specialist['title']],
            ['Credenciales', specialist['credentials']],
            ['Experiencia', specialist['experience']],
            ['Áreas de Especialización', ', '.join(specialist['specialties'])],
            ['Contacto Email', specialist['email']],
            ['Teléfono', specialist['phone']]
        ]
        
        specialist_table = Table(specialist_data, colWidths=[2.2*inch, 3.8*inch])
        specialist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f3e8ff'), colors.white]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(specialist_table)
        content.append(Spacer(1, 20))
        
        # Nota profesional de cierre
        closing_note = """
        <b>CONSIDERACIONES IMPORTANTES:</b><br/><br/>
        
        • Este resumen ha sido generado mediante análisis de inteligencia artificial avanzada<br/>
        • La evaluación se basa en la información proporcionada durante la sesión<br/>
        • Se recomienda encarecidamente el seguimiento con el profesional asignado<br/>
        • Este documento NO constituye un diagnóstico médico o psicológico formal<br/>
        • Para situaciones de emergencia, contacte servicios de salud mental inmediatamente<br/><br/>
        
        <b>Próximos pasos recomendados:</b><br/>
        1. Contactar al especialista asignado para agendar seguimiento<br/>
        2. Discutir los resultados del análisis con el profesional<br/>
        3. Recibir recomendaciones personalizadas del especialista<br/>
        4. Mantener registro del progreso durante el tratamiento
        """
        content.append(Paragraph(closing_note, styles['highlight_box']))
        
        # Footer profesional
        content.append(Spacer(1, 30))
        footer_text = f"""
        Resumen generado por Moody Bot - Sistema Avanzado de Análisis Psicológico
        Fecha de generación: {datetime.now().strftime("%d de %B de %Y a las %H:%M hrs")}
        Versión del sistema: 2.0 Professional | ID de sesión: {user_session.get('user_id', 'N/A')}
        Documento confidencial - Solo para uso del usuario y profesionales autorizados
        """
        content.append(Paragraph(footer_text, styles['footer_text']))
        
        # Construir el PDF
        doc.build(content)
        
        logger.info(f"PDF de resumen profesional generado exitosamente: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error generando PDF de resumen profesional: {e}")
        return None

def get_temp_pdf_path(filename: str) -> str:
    """Genera la ruta del archivo PDF temporal con nombre personalizado"""
    from utils.helpers import TEMP_PATH
    return os.path.join(TEMP_PATH, f"{filename}.pdf")
