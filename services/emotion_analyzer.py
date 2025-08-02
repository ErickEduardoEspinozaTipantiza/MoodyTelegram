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
            # Cargar modelo CNN con manejo de errores
            model_path = os.path.join(MODELS_PATH, "modelo_cnn.h5")
            if os.path.exists(model_path):
                try:
                    # Intentar cargar con configuración personalizada
                    import tensorflow.keras.models as models
                    custom_objects = {'batch_shape': None}  # Ignorar batch_shape
                    self.model = models.load_model(model_path, compile=False, custom_objects=custom_objects)
                    logger.info("Modelo CNN cargado exitosamente")
                except Exception as model_error:
                    logger.warning(f"Error cargando modelo CNN específico: {model_error}")
                    logger.info("Usando análisis de emociones alternativo basado en características de audio")
                    self.model = None
            
            # Cargar otros componentes
            scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Scaler cargado exitosamente")
            
            pca_path = os.path.join(MODELS_PATH, "pca.pkl")
            if os.path.exists(pca_path):
                with open(pca_path, 'rb') as f:
                    self.pca = pickle.load(f)
                logger.info("PCA cargado exitosamente")
            
            le_path = os.path.join(MODELS_PATH, "label_encoder.pkl")
            if os.path.exists(le_path):
                with open(le_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                logger.info("Label encoder cargado exitosamente")
            
            # Verificar que al menos algunos componentes estén cargados
            self.is_loaded = True  # Siempre marcar como cargado para usar análisis alternativo
            logger.info("Sistema de análisis de emociones inicializado (modo alternativo disponible)")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            self.is_loaded = True  # Usar análisis de respaldo
    
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
            
        try:
            # Extraer características básicas del audio
            features = self.extract_features(audio_path)
            if features is None:
                return self.analyze_emotion_by_audio_properties(audio_path)
            
            # Si tenemos el modelo CNN y otros componentes, usarlos
            if self.model and self.scaler and self.label_encoder:
                return self.predict_with_ml_model(features)
            else:
                # Usar análisis alternativo basado en características de audio
                return self.analyze_emotion_by_audio_properties(audio_path)
                
        except Exception as e:
            logger.error(f"Error en predicción de emoción: {e}")
            return self.analyze_emotion_by_audio_properties(audio_path)
    
    def predict_with_ml_model(self, features: np.ndarray) -> Tuple[str, float]:
        """Predicción usando el modelo ML cargado"""
        try:
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
                emotion_keys = list(EMOTIONS.keys())
                emotion_label = emotion_keys[predicted_class % len(emotion_keys)]
            
            logger.info(f"Emoción predicha con ML: {emotion_label} (confianza: {confidence:.2f})")
            return emotion_label, confidence
            
        except Exception as e:
            logger.error(f"Error en predicción ML: {e}")
            return "neutral", 0.5
    
    def analyze_emotion_by_audio_properties(self, audio_path: str) -> Tuple[str, float]:
        """Análisis alternativo basado en propiedades básicas del audio"""
        try:
            logger.info("Usando análisis de emociones alternativo basado en características de audio")
            
            # Cargar audio
            y, sr = librosa.load(audio_path, sr=16000, duration=10.0)
            
            # Calcular características básicas
            # 1. Energía RMS (relacionada con intensidad emocional)
            rms = librosa.feature.rms(y=y)
            rms_mean = np.mean(rms)
            
            # 2. Zero crossing rate (relacionado con ansiedad/agitación)
            zcr = librosa.feature.zero_crossing_rate(y)
            zcr_mean = np.mean(zcr)
            
            # 3. Spectral centroid (relacionado con brillo/energía)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            sc_mean = np.mean(spectral_centroid)
            
            # 4. Tempo aproximado
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # 5. Pausas en el audio (silencio)
            silence_ratio = np.sum(np.abs(y) < 0.01) / len(y)
            
            # Reglas heurísticas para clasificación emocional
            emotion, confidence = self.classify_by_audio_features(
                rms_mean, zcr_mean, sc_mean, tempo, silence_ratio
            )
            
            logger.info(f"Emoción detectada por análisis alternativo: {emotion} (confianza: {confidence:.2f})")
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Error en análisis alternativo: {e}")
            # Fallback final - análisis muy básico
            return self.basic_emotion_fallback(audio_path)
    
    def classify_by_audio_features(self, rms_mean: float, zcr_mean: float, 
                                 sc_mean: float, tempo: float, silence_ratio: float) -> Tuple[str, float]:
        """Clasificación basada en características de audio"""
        
        # Normalizar valores para clasificación
        rms_norm = min(rms_mean * 10, 1.0)  # Energía normalizada
        zcr_norm = min(zcr_mean * 100, 1.0)  # ZCR normalizado
        sc_norm = min(sc_mean / 3000, 1.0)   # Spectral centroid normalizado
        
        scores = {}
        
        # Reglas para cada emoción
        # Tristeza: baja energía, bajo ZCR, mucho silencio
        scores['sad'] = (1 - rms_norm) * 0.4 + (1 - zcr_norm) * 0.3 + silence_ratio * 0.3
        
        # Ansiedad: alto ZCR, energía media-alta, menos silencio
        scores['anxious'] = zcr_norm * 0.5 + rms_norm * 0.3 + (1 - silence_ratio) * 0.2
        
        # Ira: alta energía, alto ZCR, alto spectral centroid
        scores['angry'] = rms_norm * 0.4 + zcr_norm * 0.3 + sc_norm * 0.3
        
        # Calma: energía media-baja, ZCR bajo, silencio moderado
        scores['calm'] = (1 - rms_norm) * 0.3 + (1 - zcr_norm) * 0.4 + abs(silence_ratio - 0.3) * 0.3
        
        # Felicidad: energía media-alta, ZCR moderado, menos silencio
        scores['happy'] = rms_norm * 0.4 + (0.5 - abs(zcr_norm - 0.5)) * 0.3 + (1 - silence_ratio) * 0.3
        
        # Neutral: valores medios en todo
        scores['neutral'] = 1 - (abs(rms_norm - 0.5) + abs(zcr_norm - 0.5) + abs(silence_ratio - 0.4))
        
        # Encontrar la emoción con mayor score
        best_emotion = max(scores.items(), key=lambda x: x[1])
        emotion = best_emotion[0]
        confidence = min(best_emotion[1], 0.85)  # Limitar confianza máxima
        
        return emotion, confidence
    
    def basic_emotion_fallback(self, audio_path: str) -> Tuple[str, float]:
        """Fallback más básico si todo falla"""
        try:
            # Solo verificar duración y volumen muy básico
            y, sr = librosa.load(audio_path, sr=16000, duration=10.0)
            
            # Volumen promedio
            volume = np.mean(np.abs(y))
            
            if volume > 0.1:
                return "happy", 0.6  # Audio con volumen alto = emoción positiva
            elif volume < 0.02:
                return "sad", 0.6    # Audio muy bajo = tristeza
            else:
                return "neutral", 0.5 # Volumen medio = neutral
                
        except Exception:
            # Último recurso
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
