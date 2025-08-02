"""
Script para inicializar y verificar los modelos de ML
"""
import os
import sys
import logging

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from services.emotion_analyzer import emotion_analyzer
from services.ollama_client import ollama_client
from config.settings import MODELS_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_models():
    """Verifica que todos los modelos estén disponibles"""
    logger.info("🔍 Verificando modelos...")
    
    # Verificar archivos de modelo
    required_files = [
        "modelo_cnn.h5",
        "scaler.pkl", 
        "pca.pkl",
        "label_encoder.pkl"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(MODELS_PATH, file)
        if os.path.exists(file_path):
            logger.info(f"✅ {file} encontrado")
        else:
            logger.error(f"❌ {file} no encontrado")
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Archivos faltantes: {missing_files}")
        return False
    
    # Cargar analizador de emociones
    try:
        emotion_analyzer.load_models()
        if emotion_analyzer.is_loaded:
            logger.info("✅ Analizador de emociones cargado correctamente")
        else:
            logger.error("❌ Error cargando analizador de emociones")
            return False
    except Exception as e:
        logger.error(f"❌ Error inicializando analizador: {e}")
        return False
    
    # Verificar Ollama
    logger.info("🔍 Verificando Ollama...")
    ollama_client.check_availability()
    if ollama_client.is_available:
        logger.info("✅ Ollama disponible")
    else:
        logger.warning("⚠️ Ollama no disponible (usará respuestas de respaldo)")
    
    logger.info("🎉 Inicialización completada")
    return True

def test_emotion_analysis():
    """Test básico del análisis de emociones"""
    logger.info("🧪 Probando análisis de emociones...")
    
    # Crear un archivo de audio de prueba (silencio)
    try:
        import numpy as np
        import soundfile as sf
        
        # Generar 1 segundo de silencio
        sample_rate = 16000
        duration = 1
        silence = np.zeros(sample_rate * duration)
        
        test_file = "test_audio.wav"
        sf.write(test_file, silence, sample_rate)
        
        # Probar análisis
        emotion, confidence = emotion_analyzer.predict_emotion(test_file)
        logger.info(f"✅ Test de emoción: {emotion} (confianza: {confidence:.2f})")
        
        # Limpiar archivo de prueba
        if os.path.exists(test_file):
            os.remove(test_file)
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de emociones: {e}")
        return False

async def test_ollama():
    """Test básico de Ollama"""
    logger.info("🧪 Probando Ollama...")
    
    try:
        response = await ollama_client.generate_response("Hola, ¿cómo estás?")
        if response:
            logger.info(f"✅ Test de Ollama exitoso: {response[:50]}...")
            return True
        else:
            logger.warning("⚠️ Ollama respondió vacío (usando respaldo)")
            return True
    except Exception as e:
        logger.error(f"❌ Error en test de Ollama: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando verificación del sistema...")
    
    success = check_models()
    
    if success:
        logger.info("✅ Sistema listo para ejecutar")
        print("\n🤖 Para iniciar el bot, ejecuta:")
        print("python main.py")
    else:
        logger.error("❌ Sistema no está listo")
        print("\n🔧 Verifica que todos los modelos estén en la carpeta 'models/'")
        sys.exit(1)
