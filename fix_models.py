"""
Script para verificar y reparar modelos de ML
"""
import os
import sys
import logging
import pickle

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from config.settings import MODELS_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_model_compatibility():
    """Verifica la compatibilidad de los modelos"""
    logger.info("🔍 Verificando compatibilidad de modelos...")
    
    # Verificar modelo CNN
    model_path = os.path.join(MODELS_PATH, "modelo_cnn.h5")
    if os.path.exists(model_path):
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path)
            logger.info("✅ Modelo CNN compatible")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Modelo CNN incompatible: {e}")
            logger.info("💡 El bot usará análisis de emociones alternativo")
            return False
    else:
        logger.warning("⚠️ Modelo CNN no encontrado")
        return False

def test_alternative_emotion_analysis():
    """Prueba el análisis alternativo de emociones"""
    logger.info("🧪 Probando análisis alternativo de emociones...")
    
    try:
        from services.emotion_analyzer import emotion_analyzer
        
        # Cargar el analizador
        emotion_analyzer.load_models()
        
        if emotion_analyzer.is_loaded:
            logger.info("✅ Analizador de emociones alternativo funcionando")
            return True
        else:
            logger.error("❌ Error en analizador alternativo")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error probando análisis alternativo: {e}")
        return False

def create_simple_emotion_config():
    """Crea configuración simple para análisis de emociones"""
    config_path = os.path.join(MODELS_PATH, "emotion_config.pkl")
    
    # Configuración básica para análisis de emociones
    emotion_config = {
        "method": "alternative",
        "features": ["rms", "zcr", "spectral_centroid", "tempo"],
        "emotions": ["sad", "happy", "angry", "anxious", "calm", "neutral"],
        "confidence_threshold": 0.6
    }
    
    try:
        with open(config_path, 'wb') as f:
            pickle.dump(emotion_config, f)
        logger.info(f"✅ Configuración de emociones creada en {config_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando configuración: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Verificando y reparando modelos...")
    print("=" * 50)
    
    # Verificar compatibilidad
    cnn_compatible = check_model_compatibility()
    
    # Probar análisis alternativo
    alt_working = test_alternative_emotion_analysis()
    
    # Crear configuración simple
    config_created = create_simple_emotion_config()
    
    print("=" * 50)
    
    if alt_working:
        logger.info("🎉 Sistema de análisis de emociones funcionando")
        if not cnn_compatible:
            logger.info("💡 Usando método alternativo (sin CNN)")
        print("\n✅ El bot puede analizar emociones por voz")
        print("✅ Se usará análisis basado en características de audio")
    else:
        logger.error("❌ Sistema de análisis de emociones no funciona")
        print("\n⚠️ El bot funcionará sin análisis de emociones por voz")
    
    print("\n🤖 Para probar el bot completo:")
    print("python main.py")
    print("\n" + "=" * 50)
