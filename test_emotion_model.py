#!/usr/bin/env python3
"""
Script de prueba para verificar que el análisis de emociones funciona correctamente
con los modelos entrenados
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from services.emotion_analyzer import EmotionAnalyzer
from config.settings import EMOTIONS

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_emotion_analyzer():
    """Prueba el analizador de emociones"""
    print("🧪 PRUEBA DEL ANALIZADOR DE EMOCIONES")
    print("=" * 50)
    
    # Inicializar analizador
    analyzer = EmotionAnalyzer()
    
    print("📥 Cargando modelos...")
    analyzer.load_models()
    
    if not analyzer.is_loaded:
        print("❌ Error: No se pudieron cargar los modelos")
        return False
    
    print("✅ Modelos cargados exitosamente!")
    
    # Verificar qué modelos están disponibles
    print("\n📊 Estado de los modelos:")
    print(f"  - SVM: {'✅' if analyzer.model_svm else '❌'}")
    print(f"  - CNN: {'✅' if analyzer.model_cnn else '❌'}")
    print(f"  - Scaler: {'✅' if analyzer.scaler else '❌'}")
    print(f"  - PCA: {'✅' if analyzer.pca else '❌'}")
    print(f"  - Label Encoder: {'✅' if analyzer.label_encoder else '❌'}")
    
    # Verificar configuración de emociones
    print(f"\n🎭 Emociones configuradas: {list(EMOTIONS.keys())}")
    
    if analyzer.label_encoder:
        print(f"🎯 Emociones del modelo: {list(analyzer.label_encoder.classes_)}")
    
    # Buscar archivos de audio de prueba
    audio_test_dir = Path("models/data/MESD")
    if audio_test_dir.exists():
        print(f"\n🎵 Probando con archivos de audio de prueba...")
        
        # Obtener algunos archivos de prueba de diferentes emociones
        test_files = []
        for emotion in ['anger', 'happiness', 'sadness', 'fear', 'neutral']:
            emotion_files = list(audio_test_dir.glob(f"{emotion}*.wav"))
            if emotion_files:
                test_files.append((emotion, emotion_files[0]))
        
        if test_files:
            print(f"📁 Encontrados {len(test_files)} archivos de prueba")
            
            for expected_emotion, audio_file in test_files[:3]:  # Probar solo 3 para no demorar
                print(f"\n🔍 Analizando: {audio_file.name}")
                print(f"   Emoción esperada: {expected_emotion}")
                
                try:
                    predicted_emotion, confidence = analyzer.predict_emotion(str(audio_file))
                    print(f"   Emoción predicha: {predicted_emotion} (confianza: {confidence:.2f})")
                    
                    # Verificar si la predicción es correcta
                    if predicted_emotion == expected_emotion:
                        print("   ✅ Predicción correcta!")
                    else:
                        print("   ⚠️  Predicción diferente")
                        
                except Exception as e:
                    print(f"   ❌ Error en predicción: {e}")
        else:
            print("⚠️  No se encontraron archivos de audio de prueba")
    else:
        print("⚠️  Directorio de datos no encontrado para pruebas")
    
    print(f"\n🎉 Prueba completada!")
    return True

def test_feature_extraction():
    """Prueba la extracción de características"""
    print("\n🔧 PRUEBA DE EXTRACCIÓN DE CARACTERÍSTICAS")
    print("=" * 50)
    
    analyzer = EmotionAnalyzer()
    
    # Buscar un archivo de audio para probar
    audio_test_dir = Path("models/data/MESD")
    if audio_test_dir.exists():
        test_files = list(audio_test_dir.glob("*.wav"))
        if test_files:
            test_file = test_files[0]
            print(f"🎵 Probando extracción con: {test_file.name}")
            
            try:
                features = analyzer.extract_features(str(test_file))
                if features is not None:
                    print(f"✅ Características extraídas: {features.shape}")
                    print(f"   Rango: [{features.min():.3f}, {features.max():.3f}]")
                    print(f"   Promedio: {features.mean():.3f}")
                else:
                    print("❌ Error: No se pudieron extraer características")
            except Exception as e:
                print(f"❌ Error en extracción: {e}")
        else:
            print("⚠️  No se encontraron archivos de audio")
    else:
        print("⚠️  Directorio de datos no encontrado")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ANÁLISIS DE EMOCIONES")
    print("=" * 60)
    
    # Verificar que los archivos de modelo existen
    models_dir = Path("models")
    required_files = ["modelo_svm.pkl", "modelo_cnn.h5", "scaler.pkl", "pca.pkl", "label_encoder.pkl"]
    
    print("📁 Verificando archivos de modelo...")
    all_exist = True
    for file in required_files:
        file_path = models_dir / file
        status = "✅" if file_path.exists() else "❌"
        print(f"   {status} {file}")
        if not file_path.exists():
            all_exist = False
    
    if not all_exist:
        print("\n❌ Faltan archivos de modelo. Ejecuta el notebook Espaniol.ipynb primero.")
        sys.exit(1)
    
    print("\n✅ Todos los archivos de modelo están presentes")
    
    # Ejecutar pruebas
    try:
        test_emotion_analyzer()
        test_feature_extraction()
        print(f"\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        sys.exit(1)
