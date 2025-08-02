# Bot de Telegram Moody - Orientación Psicológica

## Descripción
Bot de Telegram que brinda servicios de orientación psicológica básica con análisis de emociones por voz y generación de reportes en PDF.

## Funcionalidades
- Selección de tipos de terapia
- Cuestionarios personalizados por tipo de terapia
- Análisis de emociones por voz usando modelos locales
- Generación de reportes en PDF
- Integración con Ollama LLM
- Envío de reportes por email

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno en `.env`:
```
TELEGRAM_BOT_TOKEN=8293226970:AAHns7nkSeL4SFHbmH7K6YOlglq6YAwgL1Q
OLLAMA_API_URL=http://localhost:11434
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

3. Ejecutar el bot:
```bash
python main.py
```

## Estructura del proyecto
```
├── main.py                 # Archivo principal del bot
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuraciones
│   └── therapy_questions.py # Preguntas por tipo de terapia
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py    # Manejo de comandos iniciales
│   ├── therapy_handler.py  # Selección de terapia
│   ├── voice_handler.py    # Análisis de voz
│   └── chat_handler.py     # Integración con Ollama
├── services/
│   ├── __init__.py
│   ├── emotion_analyzer.py # Análisis de emociones
│   ├── pdf_generator.py    # Generación de PDFs
│   ├── email_service.py    # Envío de emails
│   └── ollama_client.py    # Cliente para Ollama
├── models/                 # Modelos de ML
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Funciones auxiliares
└── data/
    └── user_sessions.json  # Almacenamiento temporal de sesiones
```
