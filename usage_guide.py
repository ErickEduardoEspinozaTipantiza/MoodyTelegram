#!/usr/bin/env python3
"""
Guía de uso del sistema de análisis de emociones integrado en el bot
"""

import os
from pathlib import Path

def show_usage_guide():
    """Muestra la guía de uso del sistema"""
    
    print("🤖 SISTEMA DE ANÁLISIS DE EMOCIONES - BOT MOODY")
    print("=" * 60)
    
    print("\n📊 RESUMEN DEL SISTEMA:")
    print("  • Modelo principal: SVM (81.5% precisión)")
    print("  • Modelo secundario: CNN (62.3% precisión)")
    print("  • Emociones detectadas: anger, disgust, fear, happiness, neutral, sadness")
    print("  • Características extraídas: 318 → 76 (después de PCA)")
    print("  • Dataset: MESD (Mexican Emotional Speech Database)")
    print("  • Muestras de entrenamiento: 603")
    print("  • Muestras de prueba: 130")
    
    print("\n🎯 CÓMO USAR EL BOT:")
    print("  1. Inicia el bot: python main.py")
    print("  2. En Telegram, busca tu bot y envía /start")
    print("  3. Selecciona 'Grabar mensaje de voz'")
    print("  4. Graba tu mensaje de voz con emoción")
    print("  5. El bot analizará tu emoción automáticamente")
    print("  6. Recibirás un informe con:")
    print("     • Emoción detectada")
    print("     • Nivel de confianza")
    print("     • Recomendaciones terapéuticas")
    print("     • Contacto del especialista")
    
    print("\n🔧 COMPONENTES DEL SISTEMA:")
    print("  📁 Modelos entrenados:")
    print("     • models/modelo_svm.pkl")
    print("     • models/modelo_cnn.h5")
    print("     • models/scaler.pkl")
    print("     • models/pca.pkl")
    print("     • models/label_encoder.pkl")
    
    print("\n  📝 Código principal:")
    print("     • services/emotion_analyzer.py - Análisis de emociones")
    print("     • handlers/voice_handler.py - Manejo de mensajes de voz")
    print("     • handlers/therapy_handler.py - Terapia personalizada")
    print("     • config/settings.py - Configuración")
    
    print("\n🎭 EMOCIONES DETECTADAS:")
    emotions = {
        "anger": "Ira - Señales de frustración o enfado",
        "disgust": "Disgusto - Rechazo o aversión",
        "fear": "Miedo - Ansiedad o temor",
        "happiness": "Felicidad - Alegría y bienestar",
        "neutral": "Neutral - Estado emocional estable",
        "sadness": "Tristeza - Melancolía o abatimiento"
    }
    
    for emotion, description in emotions.items():
        print(f"     • {emotion}: {description}")
    
    print("\n📈 PRECISIÓN POR EMOCIÓN (Modelo SVM):")
    print("     • anger: 89% precisión")
    print("     • disgust: 80% precisión") 
    print("     • fear: 90% precisión")
    print("     • happiness: 82% precisión")
    print("     • neutral: 89% precisión")
    print("     • sadness: 67% precisión")
    
    print("\n⚙️ CARACTERÍSTICAS TÉCNICAS:")
    print("     • Frecuencia de muestreo: 22kHz")
    print("     • Características MFCC: 13 coeficientes")
    print("     • Características Chroma: 12 coeficientes")
    print("     • Mel Spectrogram: 128 bandas")
    print("     • Características temporales: ZCR, RMS, Pitch")
    print("     • Características espectrales: Centroide, Rolloff")
    
    print("\n🚀 PRÓXIMAS MEJORAS:")
    print("     • Entrenamiento con más datos")
    print("     • Detección de emociones mixtas")
    print("     • Análisis temporal de emociones")
    print("     • Personalización por usuario")
    
    print("\n📞 SOPORTE:")
    print("     • Email: crisgeopro2003@gmail.com")
    print("     • Logs: Revisa la consola para diagnósticos")
    print("     • Test: python test_emotion_model.py")
    
    print("\n✅ SISTEMA LISTO PARA USAR!")
    print("   El bot ya puede analizar emociones en tiempo real.")

if __name__ == "__main__":
    show_usage_guide()
