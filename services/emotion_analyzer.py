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
        self.model_cnn = None
        self.model_svm = None
        self.scaler = None
        self.pca = None
        self.label_encoder = None
        self.is_loaded = False
        
    def load_models(self):
        """Carga todos los modelos necesarios"""
        try:
            # Cargar modelo CNN con manejo robusto de errores
            model_path = os.path.join(MODELS_PATH, "modelo_cnn.h5")
            if os.path.exists(model_path):
                try:
                    # Intentar carga directa primero
                    import tensorflow.keras.models as models
                    self.model_cnn = models.load_model(model_path, compile=False)
                    logger.info("Modelo CNN cargado exitosamente")
                except Exception as model_error:
                    logger.warning(f"Error cargando modelo CNN directo: {model_error}")
                    try:
                        # Intentar con configuración personalizada más simple
                        self.model_cnn = models.load_model(
                            model_path, 
                            compile=False, 
                            custom_objects={'batch_shape': None}
                        )
                        logger.info("Modelo CNN cargado con configuración personalizada")
                    except Exception as fallback_error:
                        logger.warning(f"Error cargando modelo CNN con fallback: {fallback_error}")
                        logger.info("Continuando sin modelo CNN - usando análisis alternativo")
                        self.model_cnn = None
            else:
                logger.warning(f"Archivo de modelo CNN no encontrado: {model_path}")
                self.model_cnn = None

            # Cargar modelo SVM (nuevo - mejor rendimiento)
            svm_path = os.path.join(MODELS_PATH, "modelo_svm.pkl")
            if os.path.exists(svm_path):
                try:
                    with open(svm_path, 'rb') as f:
                        self.model_svm = pickle.load(f)
                    logger.info("Modelo SVM cargado exitosamente")
                except Exception as e:
                    logger.error(f"Error cargando modelo SVM: {e}")
                    self.model_svm = None
            else:
                logger.warning(f"Archivo de modelo SVM no encontrado: {svm_path}")
            
            # Cargar scaler
            scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")
            if os.path.exists(scaler_path):
                try:
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    logger.info("Scaler cargado exitosamente")
                except Exception as e:
                    logger.error(f"Error cargando scaler: {e}")
                    self.scaler = None
            
            # Cargar PCA
            pca_path = os.path.join(MODELS_PATH, "pca.pkl")
            if os.path.exists(pca_path):
                try:
                    with open(pca_path, 'rb') as f:
                        self.pca = pickle.load(f)
                    logger.info("PCA cargado exitosamente")
                except Exception as e:
                    logger.error(f"Error cargando PCA: {e}")
                    self.pca = None
            
            # Cargar label encoder
            le_path = os.path.join(MODELS_PATH, "label_encoder.pkl")
            if os.path.exists(le_path):
                try:
                    with open(le_path, 'rb') as f:
                        self.label_encoder = pickle.load(f)
                    logger.info("Label encoder cargado exitosamente")
                except Exception as e:
                    logger.error(f"Error cargando label encoder: {e}")
                    self.label_encoder = None
            
            # Verificar que al menos algunos componentes estén cargados
            self.is_loaded = True  # Siempre marcar como cargado para usar análisis alternativo
            
            if self.model_svm is not None:
                logger.info("Sistema de análisis de emociones inicializado con modelo SVM (principal)")
            elif self.model_cnn is not None:
                logger.info("Sistema de análisis de emociones inicializado con modelo CNN")
            else:
                logger.info("Sistema de análisis de emociones inicializado (modo alternativo disponible)")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            self.is_loaded = True  # Usar análisis de respaldo
    
    def extract_features(self, audio_path: str, sample_rate: int = 22050) -> Optional[np.ndarray]:
        """Extrae características del audio para el análisis - EXACTAMENTE como en el notebook"""
        try:
            # Configuración idéntica al notebook
            n_mfcc = 13
            n_chroma = 12
            frame_length = 2048
            hop_length = 512
            
            # Cargar audio con la misma configuración del notebook
            y, sr = librosa.load(audio_path, sr=sample_rate)
            
            # Lista para almacenar todas las características
            features_list = []
            
            try:
                # 1. MFCC (13 mean + 13 std = 26 características)
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, 
                                           n_fft=frame_length, hop_length=hop_length)
                mfcc_mean = np.mean(mfcc, axis=1)
                mfcc_std = np.std(mfcc, axis=1)
                features_list.extend([mfcc_mean, mfcc_std])
            except Exception as e:
                logger.warning(f"Error extrayendo MFCC: {e}")
                features_list.extend([np.zeros(13), np.zeros(13)])
            
            try:
                # 2. CHROMA (12 mean + 12 std = 24 características)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr, 
                                                   n_fft=frame_length, hop_length=hop_length)
                chroma_mean = np.mean(chroma, axis=1)
                chroma_std = np.std(chroma, axis=1)
                features_list.extend([chroma_mean, chroma_std])
            except Exception as e:
                logger.warning(f"Error extrayendo chroma: {e}")
                features_list.extend([np.zeros(12), np.zeros(12)])
            
            try:
                # 3. MEL SPECTROGRAM (128 mean + 128 std = 256 características)
                mel_spec = librosa.feature.melspectrogram(y=y, sr=sr,
                                                         n_fft=frame_length, hop_length=hop_length)
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                mel_mean = np.mean(mel_spec_db, axis=1)
                mel_std = np.std(mel_spec_db, axis=1)
                features_list.extend([mel_mean, mel_std])
            except Exception as e:
                logger.warning(f"Error extrayendo mel spectrogram: {e}")
                features_list.extend([np.zeros(128), np.zeros(128)])
            
            try:
                # 4. ZERO CROSSING RATE (2 características)
                zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, 
                                                       hop_length=hop_length)
                zcr_mean = np.mean(zcr)
                zcr_std = np.std(zcr)
                features_list.append(np.array([zcr_mean, zcr_std]))
            except Exception as e:
                logger.warning(f"Error extrayendo ZCR: {e}")
                features_list.append(np.zeros(2))
            
            try:
                # 5. RMS ENERGY (2 características)
                rms = librosa.feature.rms(y=y, frame_length=frame_length, 
                                         hop_length=hop_length)
                rms_mean = np.mean(rms)
                rms_std = np.std(rms)
                features_list.append(np.array([rms_mean, rms_std]))
            except Exception as e:
                logger.warning(f"Error extrayendo RMS: {e}")
                features_list.append(np.zeros(2))
            
            try:
                # 6. PITCH (4 características)
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=600)
                pitch_values = []
                for t in range(pitches.shape[1]):
                    index = magnitudes[:, t].argmax()
                    pitch = pitches[index, t]
                    if pitch > 0:
                        pitch_values.append(pitch)
                
                if len(pitch_values) > 0:
                    pitch_mean = np.mean(pitch_values)
                    pitch_std = np.std(pitch_values)
                    pitch_min = np.min(pitch_values)
                    pitch_max = np.max(pitch_values)
                else:
                    pitch_mean = pitch_std = pitch_min = pitch_max = 0
                    
                features_list.append(np.array([pitch_mean, pitch_std, pitch_min, pitch_max]))
            except Exception as e:
                logger.warning(f"Error extrayendo pitch: {e}")
                features_list.append(np.zeros(4))
            
            try:
                # 7. SPECTRAL CENTROID (2 características)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                sc_mean = np.mean(spectral_centroid)
                sc_std = np.std(spectral_centroid)
                features_list.append(np.array([sc_mean, sc_std]))
            except Exception as e:
                logger.warning(f"Error extrayendo spectral centroid: {e}")
                features_list.append(np.zeros(2))
            
            try:
                # 8. SPECTRAL ROLLOFF (2 características)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                sr_mean = np.mean(spectral_rolloff)
                sr_std = np.std(spectral_rolloff)
                features_list.append(np.array([sr_mean, sr_std]))
            except Exception as e:
                logger.warning(f"Error extrayendo spectral rolloff: {e}")
                features_list.append(np.zeros(2))
            
            # Concatenar todas las características (debería dar 318 características totales)
            features = np.concatenate(features_list)
            
            logger.debug(f"Características extraídas: {features.shape}")
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características del audio: {e}")
            # Retornar vector de características por defecto (318 características)
            return np.zeros(318)
    
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
            
            # Si tenemos modelos ML y otros componentes, usarlos (SVM prioritario)
            if (self.model_svm or self.model_cnn) and self.scaler and self.label_encoder:
                return self.predict_with_ml_model(features)
            else:
                # Usar análisis alternativo basado en características de audio
                return self.analyze_emotion_by_audio_properties(audio_path)
                
        except Exception as e:
            logger.error(f"Error en predicción de emoción: {e}")
            return self.analyze_emotion_by_audio_properties(audio_path)
    
    def predict_with_ml_model(self, features: np.ndarray) -> Tuple[str, float]:
        """Predicción usando el modelo ML cargado - Compatible con el notebook"""
        try:
            # Asegurar que las características tengan la forma correcta
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Normalizar características
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
                logger.warning("Scaler no disponible, usando características sin normalizar")
            
            # Aplicar PCA si está disponible
            if self.pca is not None:
                features_pca = self.pca.transform(features_scaled)
                logger.debug(f"Características después de PCA: {features_pca.shape}")
            else:
                features_pca = features_scaled
                logger.warning("PCA no disponible")
            
            # Intentar predicción con SVM primero (mejor rendimiento: 81.5%)
            if self.model_svm is not None:
                try:
                    prediction = self.model_svm.predict(features_pca)
                    prediction_proba = self.model_svm.predict_proba(features_pca) if hasattr(self.model_svm, 'predict_proba') else None
                    
                    # Obtener la clase predicha
                    predicted_class = prediction[0]
                    
                    # Calcular confianza
                    if prediction_proba is not None:
                        confidence = float(np.max(prediction_proba[0]))
                    else:
                        confidence = 0.8  # Confianza por defecto para SVM
                    
                    # Convertir a etiqueta de emoción
                    if hasattr(self.label_encoder, 'classes_'):
                        emotion_label = self.label_encoder.classes_[predicted_class]
                    else:
                        emotion_keys = list(EMOTIONS.keys())
                        emotion_label = emotion_keys[predicted_class % len(emotion_keys)]
                    
                    logger.info(f"Emoción predicha con SVM: {emotion_label} (confianza: {confidence:.2f})")
                    return emotion_label, confidence
                    
                except Exception as svm_error:
                    logger.warning(f"Error en predicción SVM: {svm_error}")
                    # Continuar con CNN si está disponible
            
            # Intentar predicción con CNN si SVM falla o no está disponible
            if self.model_cnn is not None:
                try:
                    # Preparar datos para CNN: (samples, features, 1)
                    features_cnn = features_pca.reshape(features_pca.shape[0], features_pca.shape[1], 1)
                    logger.debug(f"Forma para CNN: {features_cnn.shape}")
                    
                    # Verificar que las dimensiones sean compatibles con el modelo CNN
                    if features_cnn.shape[1] < 2:  # Si PCA resultó en muy pocas características
                        logger.warning(f"Muy pocas características para CNN ({features_cnn.shape[1]}), usando análisis alternativo")
                        raise ValueError("Dimensiones insuficientes para CNN")
                    
                    prediction = self.model_cnn.predict(features_cnn, verbose=0)
                    
                    # Obtener la clase con mayor probabilidad
                    predicted_class = np.argmax(prediction[0])
                    confidence = float(np.max(prediction[0]))
                    
                    # Convertir a etiqueta de emoción
                    if hasattr(self.label_encoder, 'classes_'):
                        emotion_label = self.label_encoder.classes_[predicted_class]
                    else:
                        emotion_keys = list(EMOTIONS.keys())
                        emotion_label = emotion_keys[predicted_class % len(emotion_keys)]
                    
                    logger.info(f"Emoción predicha con CNN: {emotion_label} (confianza: {confidence:.2f})")
                    return emotion_label, confidence
                    
                except Exception as cnn_error:
                    logger.warning(f"Error en predicción CNN: {cnn_error}")
                    # Continuar con análisis alternativo
            
            # Fallback a análisis alternativo si no hay modelos ML disponibles
            logger.info("Usando análisis de emociones alternativo basado en características extraídas")
            return self.analyze_emotion_by_features_fallback(features_pca)
            
        except Exception as e:
            logger.error(f"Error en predicción ML: {e}")
            return "neutral", 0.5
    
    def analyze_emotion_by_features_fallback(self, features: np.ndarray) -> Tuple[str, float]:
        """Análisis alternativo basado en características extraídas cuando falla ML"""
        try:
            # Usar las características extraídas para análisis heurístico
            if len(features.flatten()) == 0:
                return "neutral", 0.4
            
            # Tomar las características (post-PCA si está disponible)
            feat_flat = features.flatten()
            
            # Análisis heurístico basado en estadísticas de las características
            mean_val = np.mean(feat_flat)
            std_val = np.std(feat_flat)
            energy = np.sum(feat_flat ** 2)
            
            # Reglas heurísticas simples - coincidiendo con emociones del modelo entrenado
            emotion_scores = {
                'happiness': 0.0,
                'sadness': 0.0,
                'anger': 0.0,
                'fear': 0.0,
                'disgust': 0.0,
                'neutral': 0.2
            }
            
            # Análisis basado en energía y variabilidad
            if energy > np.percentile(feat_flat, 75):  # Alta energía
                emotion_scores['happiness'] += 0.3
                emotion_scores['anger'] += 0.2
            elif energy < np.percentile(feat_flat, 25):  # Baja energía
                emotion_scores['sadness'] += 0.3
                emotion_scores['neutral'] += 0.2
            
            if std_val > np.percentile(feat_flat, 75):  # Alta variabilidad
                emotion_scores['fear'] += 0.3
                emotion_scores['anger'] += 0.2
            elif std_val < np.percentile(feat_flat, 25):  # Baja variabilidad
                emotion_scores['neutral'] += 0.3
                emotion_scores['sadness'] += 0.2
            
            # Seleccionar emoción con mayor score
            predicted_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            emotion_label = predicted_emotion[0]
            confidence = max(predicted_emotion[1], 0.3)  # Mínimo 30% confianza
            
            logger.info(f"Emoción predicha (análisis de características): {emotion_label} (confianza: {confidence:.2f})")
            return emotion_label, confidence
            
        except Exception as e:
            logger.error(f"Error en análisis de características: {e}")
            return "neutral", 0.4
    
    def analyze_emotion_by_audio_properties(self, audio_path: str) -> Tuple[str, float]:
        """Análisis alternativo basado en propiedades básicas del audio"""
        try:
            logger.info("Usando análisis de emociones alternativo basado en características de audio")
            
            # Cargar audio de manera robusta
            y, sr = librosa.load(audio_path, sr=16000, duration=10.0)
            
            if len(y) == 0:
                logger.warning("Audio vacío, retornando emoción neutral")
                return "neutral", 0.3
            
            # Calcular características básicas de manera robusta
            features = {}
            
            try:
                # Energía RMS
                rms_energy = np.sqrt(np.mean(y**2))
                features['energy'] = rms_energy
            except:
                features['energy'] = 0.0
            
            try:
                # Tasa de cruces por cero
                zcr = np.mean(librosa.feature.zero_crossing_rate(y))
                features['zcr'] = zcr
            except:
                features['zcr'] = 0.0
            
            try:
                # Centroide espectral (brillo)
                spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                features['brightness'] = spectral_centroid
            except:
                features['brightness'] = 1000.0  # Valor por defecto
            
            try:
                # Variabilidad de pitch (aproximación con autocorrelación)
                pitch_variation = np.std(y)
                features['pitch_var'] = pitch_variation
            except:
                features['pitch_var'] = 0.1
            
            try:
                # Tempo aproximado usando intervalos entre picos
                rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
                rms_mean = np.mean(rms)
                features['tempo_approx'] = rms_mean * 1000  # Escalar para mejor discriminación
            except:
                features['tempo_approx'] = 120.0
            
            # Análisis de emociones basado en características
            emotion_scores = {
                'happy': 0.0,
                'sad': 0.0,
                'angry': 0.0,
                'anxious': 0.0,
                'calm': 0.0,
                'fear': 0.0,
                'neutral': 0.2  # Base mínima para neutral
            }
            
            # Reglas heurísticas mejoradas
            energy = features['energy']
            zcr = features['zcr']
            brightness = features['brightness']
            pitch_var = features['pitch_var']
            tempo = features['tempo_approx']
            
            # Happy: Alta energía, alta frecuencia, estable
            if energy > 0.05 and brightness > 1500 and pitch_var < 0.3:
                emotion_scores['happy'] += 0.4
            
            # Sad: Baja energía, bajas frecuencias, estable
            if energy < 0.03 and brightness < 1000 and zcr < 0.1:
                emotion_scores['sad'] += 0.4
            
            # Angry: Alta energía, mucha variación, frecuencias medias-altas
            if energy > 0.06 and pitch_var > 0.4 and brightness > 1200:
                emotion_scores['angry'] += 0.4
            
            # Anxious: Energía media, mucha variación en pitch
            if 0.03 < energy < 0.06 and pitch_var > 0.3 and zcr > 0.08:
                emotion_scores['anxious'] += 0.4
            
            # Calm: Energía baja-media, poca variación, frecuencias medias
            if 0.02 < energy < 0.04 and pitch_var < 0.2 and 800 < brightness < 1200:
                emotion_scores['calm'] += 0.4
            
            # Fear: Energía variable, alta variación, frecuencias altas
            if pitch_var > 0.35 and brightness > 1400 and zcr > 0.09:
                emotion_scores['fear'] += 0.4
            
            # Ajustes adicionales basados en combinaciones
            if energy > 0.1:  # Muy alta energía
                emotion_scores['angry'] += 0.2
                emotion_scores['happy'] += 0.1
            
            if energy < 0.02:  # Muy baja energía
                emotion_scores['sad'] += 0.3
                emotion_scores['calm'] += 0.1
            
            # Normalizar scores para que sumen 1
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                emotion_scores = {k: v/total_score for k, v in emotion_scores.items()}
            
            # Seleccionar emoción con mayor score
            predicted_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            emotion_label = predicted_emotion[0]
            confidence = predicted_emotion[1]
            
            # Asegurar confianza mínima
            confidence = max(confidence, 0.3)
            
            logger.info(f"Emoción predicha (análisis alternativo): {emotion_label} (confianza: {confidence:.2f})")
            logger.debug(f"Características: energia={energy:.3f}, zcr={zcr:.3f}, brillo={brightness:.1f}")
            
            return emotion_label, confidence
            
        except Exception as e:
            logger.error(f"Error en análisis alternativo: {e}")
            logger.info("Retornando emoción neutral por defecto")
            return "neutral", 0.4
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
