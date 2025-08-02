import numpy as np
import librosa
import tensorflow as tf
import pickle
import logging
from typing import Tuple, Optional
import os
from config.settings import MODELS_PATH, EMOTIONS

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.pca = None
        self.label_encoder = None
        self.is_loaded = False
        
    def load_models(self):
        """Carga todos los modelos necesarios"""
        try:
            # Cargar modelo CNN
            model_path = os.path.join(MODELS_PATH, "modelo_cnn.h5")
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Modelo CNN cargado exitosamente")
            
            # Cargar scaler
            scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Scaler cargado exitosamente")
            
            # Cargar PCA
            pca_path = os.path.join(MODELS_PATH, "pca.pkl")
            if os.path.exists(pca_path):
                with open(pca_path, 'rb') as f:
                    self.pca = pickle.load(f)
                logger.info("PCA cargado exitosamente")
            
            # Cargar label encoder
            le_path = os.path.join(MODELS_PATH, "label_encoder.pkl")
            if os.path.exists(le_path):
                with open(le_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                logger.info("Label encoder cargado exitosamente")
            
            # Verificar que todos los modelos estén cargados
            if all([self.model, self.scaler, self.pca, self.label_encoder]):
                self.is_loaded = True
                logger.info("Todos los modelos cargados correctamente")
            else:
                logger.warning("Algunos modelos no pudieron ser cargados")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            self.is_loaded = False
    
    def extract_features(self, audio_path: str, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """Extrae características del audio para el análisis"""
        try:
            # Cargar audio
            y, sr = librosa.load(audio_path, sr=sample_rate, duration=10.0)
            
            # Extraer características MFCC
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            # Extraer características adicionales
            # Spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_centroid_mean = np.mean(spectral_centroid)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            zcr_mean = np.mean(zcr)
            
            # RMS energy
            rms = librosa.feature.rms(y=y)
            rms_mean = np.mean(rms)
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            rolloff_mean = np.mean(rolloff)
            
            # Combinar todas las características
            features = np.concatenate([
                mfccs_mean,
                [spectral_centroid_mean, zcr_mean, rms_mean, rolloff_mean]
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características del audio: {e}")
            return None
    
    def predict_emotion(self, audio_path: str) -> Tuple[str, float]:
        """Predice la emoción del audio"""
        if not self.is_loaded:
            logger.warning("Modelos no cargados, intentando cargar...")
            self.load_models()
            
        if not self.is_loaded:
            logger.error("No se pudieron cargar los modelos")
            return "neutral", 0.5
        
        try:
            # Extraer características
            features = self.extract_features(audio_path)
            if features is None:
                return "neutral", 0.5
            
            # Normalizar características
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Aplicar PCA si está disponible
            if self.pca:
                features_pca = self.pca.transform(features_scaled)
            else:
                features_pca = features_scaled
            
            # Hacer predicción
            prediction = self.model.predict(features_pca, verbose=0)
            
            # Obtener la clase con mayor probabilidad
            predicted_class = np.argmax(prediction[0])
            confidence = float(np.max(prediction[0]))
            
            # Convertir a etiqueta de emoción
            if hasattr(self.label_encoder, 'classes_'):
                emotion_label = self.label_encoder.classes_[predicted_class]
            else:
                # Fallback si no hay label encoder
                emotion_keys = list(EMOTIONS.keys())
                emotion_label = emotion_keys[predicted_class % len(emotion_keys)]
            
            logger.info(f"Emoción predicha: {emotion_label} (confianza: {confidence:.2f})")
            return emotion_label, confidence
            
        except Exception as e:
            logger.error(f"Error en predicción de emoción: {e}")
            return "neutral", 0.5
    
    def get_emotion_description(self, emotion: str, confidence: float) -> str:
        """Genera una descripción de la emoción detectada"""
        emotion_name = EMOTIONS.get(emotion, "Emoción desconocida")
        
        confidence_level = ""
        if confidence > 0.8:
            confidence_level = "muy alta"
        elif confidence > 0.6:
            confidence_level = "alta"
        elif confidence > 0.4:
            confidence_level = "moderada"
        else:
            confidence_level = "baja"
        
        return f"Detecté **{emotion_name}** con confianza {confidence_level} ({confidence*100:.1f}%)"

# Instancia global del analizador
emotion_analyzer = EmotionAnalyzer()
