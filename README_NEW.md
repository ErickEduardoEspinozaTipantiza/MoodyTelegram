# 🤖 Bot Moody - Análisis de Emociones por Voz con IA

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-orange.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.6.1-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

*Bot inteligente de Telegram que analiza emociones en tiempo real mediante modelos de Machine Learning entrenados, proporcionando terapia personalizada y recomendaciones profesionales.*

[🚀 Instalación](#-instalación) • [🧠 Modelos IA](#-sistema-de-análisis-de-emociones) • [📱 Uso](#-uso-del-bot) • [🧪 Pruebas](#-pruebas-y-validación) • [📁 Estructura](#-estructura-del-proyecto)

</div>

---

## 🎯 Características Principales

### 🧠 **Análisis de Emociones con IA**
- **Modelo SVM entrenado**: 81.5% precisión en detección emocional
- **6 emociones detectadas**: anger, disgust, fear, happiness, neutral, sadness
- **Dataset MESD**: 862 muestras de audio en español
- **Análisis en tiempo real**: Predicción instantánea de estado emocional

### 🎭 **Terapia Personalizada**
- **4 tipos de terapia**: Familiar, Pareja, Individual, Adolescentes  
- **Especialistas reales**: Contacto directo con profesionales
- **Reportes en PDF**: Análisis detallado y recomendaciones
- **Seguimiento emocional**: Historial de estados emocionales

### 🤖 **IA Conversacional**
- **Integración Ollama**: Chat empático y contextual
- **Respuestas personalizadas**: Basadas en el estado emocional detectado
- **Soporte 24/7**: Disponible en cualquier momento

---

## 🧠 Sistema de Análisis de Emociones

### 📊 **Modelos Entrenados**

| Modelo | Precisión | Uso | Estado |
|--------|-----------|-----|--------|
| **SVM (Principal)** | **81.5%** | Predicción principal | ✅ Activo |
| CNN (Secundario) | 62.3% | Fallback | ✅ Activo |
| Análisis Heurístico | ~60% | Último recurso | ✅ Activo |

### 🎯 **Precisión por Emoción (SVM)**

| Emoción | Precisión | Recall | F1-Score | Muestras |
|---------|-----------|--------|----------|----------|
| **Fear** | 90% | 90% | 90% | 21 |
| **Anger** | 89% | 73% | 80% | 22 |
| **Neutral** | 89% | 77% | 83% | 22 |
| **Happiness** | 82% | 86% | 84% | 21 |
| **Disgust** | 80% | 73% | 76% | 22 |
| **Sadness** | 67% | 91% | 77% | 22 |

### 🔧 **Características Técnicas**
- **Características extraídas**: 318 → 76 (post-PCA)
- **MFCC**: 13 coeficientes + estadísticas
- **Chroma**: 12 características cromáticas  
- **Mel Spectrogram**: 128 bandas de frecuencia
- **Temporales**: ZCR, RMS Energy, Pitch analysis
- **Espectrales**: Centroide, Rolloff

---

## 🚀 Instalación

### 📋 Requisitos Previos
- Python 3.11+
- Token de Bot de Telegram
- Ollama (opcional)

### ⚡ Instalación Rápida
```bash
# Clonar repositorio
git clone [tu-repositorio]
cd 1BotTelegram

# Instalar dependencias
pip install -r requirements.txt

# Configurar token del bot
# Editar config/settings.py con tu token

# ¡Listo para usar!
python main.py
```

### 🧪 Verificar Instalación
```bash
# Probar el sistema de análisis
python test_emotion_model.py

# Ver guía completa de uso
python usage_guide.py
```

---

## 📱 Uso del Bot

### 🎮 **Comandos Principales**
- `/start` - Iniciar conversación
- `/help` - Mostrar ayuda

### 🗣️ **Flujo de Análisis Emocional**

1. **📱 Iniciar**: Envía `/start` al bot
2. **🎭 Seleccionar**: Elige tipo de terapia  
3. **🎤 Grabar**: Envía mensaje de voz (máx. 10s)
4. **🧠 Análisis**: IA detecta tu emoción automáticamente
5. **📊 Reporte**: Recibe análisis detallado
6. **👨‍⚕️ Profesional**: Contacta especialista recomendado

### 👨‍👩‍👧‍👦 **Especialistas Disponibles**

| Terapia | Especialista | Precisión Foco |
|---------|--------------|----------------|
| **Familiar** | Dra. María Elena Vásquez | Dinámicas familiares |
| **Pareja** | Dr. Carlos Alberto Mendoza | Relaciones de pareja |
| **Individual** | Dra. Ana Sofía Herrera | Crecimiento personal |
| **Adolescentes** | Dr. Roberto Andrés Castro | Psicología del desarrollo |

---

## 🧪 Pruebas y Validación

### ✅ **Verificación del Sistema**
```bash
# Prueba completa del sistema
python test_emotion_model.py

# Resultado esperado:
# ✅ Modelos cargados exitosamente
# ✅ Predicciones correctas (3/3)
# ✅ Extracción de características OK
```

### 🔄 **Re-entrenar Modelos**
```bash
# Abrir notebook de entrenamiento
jupyter notebook models/Espaniol.ipynb

# O usar VS Code
code models/Espaniol.ipynb
```

### 📈 **Resultados de Prueba**
- **Precisión global**: 82% (130 muestras de prueba)
- **Tiempo de predicción**: ~0.5 segundos
- **Características procesadas**: 318 → 76 dimensiones
- **Emociones detectadas**: 6 categorías

---

## 📁 Estructura del Proyecto

```
🤖 1BotTelegram/
├── 🧠 models/                    # Modelos entrenados
│   ├── 📊 Espaniol.ipynb        # Notebook de entrenamiento  
│   ├── 🎯 modelo_svm.pkl        # Modelo SVM (principal)
│   ├── 🧮 modelo_cnn.h5         # Modelo CNN (secundario)
│   ├── ⚖️ scaler.pkl            # Normalizador
│   ├── 📉 pca.pkl               # Reductor PCA
│   ├── 🏷️ label_encoder.pkl     # Codificador etiquetas
│   └── 🎵 data/MESD/            # Dataset de audio
├── 🎭 services/
│   ├── 🧠 emotion_analyzer.py   # Motor de análisis IA
│   ├── 🤖 ollama_client.py      # Cliente IA conversacional
│   ├── 📄 pdf_generator.py      # Generador reportes
│   └── 📧 email_service.py      # Servicio email
├── 🎛️ handlers/
│   ├── 🗣️ voice_handler.py      # Análisis de voz
│   ├── 💬 chat_handler.py       # Chat con IA
│   ├── 🏥 therapy_handler.py    # Lógica terapéutica
│   └── ▶️ start_handler.py      # Comandos iniciales
├── ⚙️ config/
│   ├── 🔧 settings.py           # Configuración principal
│   └── ❓ therapy_questions.py  # Preguntas terapéuticas
├── 🧪 test_emotion_model.py     # Pruebas del sistema
├── 📖 usage_guide.py            # Guía de uso
├── 🚀 main.py                   # Punto de entrada
└── 📋 requirements.txt          # Dependencias
```

---

## 🔧 Configuración Avanzada

### 🎛️ **Variables del Sistema**
```python
# config/settings.py
EMOTIONS = {
    "anger": "Ira",
    "disgust": "Disgusto", 
    "fear": "Miedo",
    "happiness": "Felicidad",
    "neutral": "Neutral",
    "sadness": "Tristeza"
}

# Parámetros de audio
MAX_AUDIO_DURATION = 10  # segundos
AUDIO_SAMPLE_RATE = 22050  # Hz
```

### 📊 **Pipeline de Predicción**
```python
# Flujo de análisis emocional:
Audio → Características (318) → Normalización → PCA (76) → SVM → Emoción
```

### 🔍 **Logging y Debug**
```python
# Logs detallados disponibles:
# - Carga de modelos
# - Análisis de audio
# - Predicciones y confianza
# - Errores y excepciones
```

---

## 🛠️ Solución de Problemas

### ❌ **Problemas Comunes**

| Problema | Solución |
|----------|----------|
| Modelos no encontrados | Ejecutar `jupyter notebook models/Espaniol.ipynb` |
| TensorFlow no instalado | `pip install tensorflow` |
| Audio no compatible | Usar WAV/OGG, máx. 10s, 22kHz |
| Error de versión sklearn | Compatible con versiones 1.3.2+ |

### 🔧 **Debug Avanzado**
```bash
# Verificar estado completo
python test_emotion_model.py

# Ver logs en tiempo real
python main.py  # Revisar consola

# Test de características específicas  
python -c "from services.emotion_analyzer import EmotionAnalyzer; a=EmotionAnalyzer(); a.load_models()"
```

---

## 📈 Rendimiento y Métricas

### ⚡ **Rendimiento en Tiempo Real**
- **Tiempo de análisis**: ~0.5 segundos por audio
- **Memoria utilizada**: ~200MB (modelos cargados)
- **CPU**: Optimizado para procesadores modernos
- **Precisión promedio**: 82% en datos de prueba

### 📊 **Métricas de Calidad**
- **Datos de entrenamiento**: 603 muestras (70%)
- **Datos de validación**: 129 muestras (15%)  
- **Datos de prueba**: 130 muestras (15%)
- **Balance de clases**: Bien balanceado (~143 muestras/emoción)

---

## 🤝 Contribución y Desarrollo

### 🔄 **Para Desarrolladores**
```bash
# Fork y clonar
git clone [tu-fork]
cd 1BotTelegram

# Crear rama feature
git checkout -b nueva-caracteristica

# Desarrollar y commitear
git commit -am "Agregar nueva característica"

# Push y Pull Request
git push origin nueva-caracteristica
```

### 🚀 **Roadmap de Mejoras**
- [ ] Detección de emociones mixtas
- [ ] Análisis temporal (cambios emocionales)
- [ ] Personalización por usuario
- [ ] Dashboard web para terapeutas
- [ ] API REST para integraciones
- [ ] Soporte para más idiomas

---

## 📞 Soporte y Contacto

### 🆘 **Obtener Ayuda**
- **Email**: crisgeopro2003@gmail.com
- **Issues**: [GitHub Issues](tu-repositorio/issues)
- **Documentación**: Archivos `*.py` documentados

### 📚 **Recursos Adicionales**
- **Dataset MESD**: Mexican Emotional Speech Database
- **Papers**: Análisis de emociones por voz en español
- **Tutoriales**: Machine Learning para análisis de audio

---

## 📄 Licencia y Agradecimientos

### 📜 **Licencia**
Este proyecto está bajo la **Licencia MIT**. Ver `LICENSE` para detalles.

### 🙏 **Agradecimientos**
- **MESD**: Por el dataset de emociones en español
- **Librosa**: Procesamiento de señales de audio
- **Scikit-learn**: Modelos de Machine Learning
- **TensorFlow**: Redes neuronales profundas
- **python-telegram-bot**: Integración con Telegram

---

<div align="center">

## 🎉 ¡Sistema Listo!

**El bot está entrenado y listo para analizar emociones en tiempo real**

```bash
python main.py
```

*Desarrollado con ❤️ para ayudar en salud mental*

</div>
