"""
Optimized Emotion Detector dengan Confidence Calibration
Menggunakan FER + Ensemble untuk hasil lebih stabil
"""

from fer import FER
import cv2
import numpy as np
from collections import Counter

class EmotionDetectorFER:
    def __init__(self):
        # Initialize FER detector dengan MTCNN
        self.detector = FER(mtcnn=True)
        
        # Simplified emotions
        self.emotions_map = {
            'happy': 'positive',
            'surprise': 'positive',
            'neutral': 'neutral',
            'sad': 'negative',
            'angry': 'negative',
            'fear': 'negative',
            'disgust': 'negative'
        }
        
        self.emotion_emoji = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😔'
        }
        
        self.emotion_indonesian = {
            'positive': 'Baik',
            'neutral': 'Netral',
            'negative': 'Kurang Baik'
        }
        
        self.emotion_color = {
            'positive': '#22c55e',
            'neutral': '#6b7280',
            'negative': '#ef4444'
        }
    
    def preprocess_image(self, image):
        """Enhanced preprocessing untuk emotion detection"""
        try:
            # Ensure RGB
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Contrast enhancement
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # Merge back
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            # Slight sharpening
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]]) / 9
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
        except:
            return image
    
    def detect_emotion_single(self, image):
        """Single detection"""
        try:
            # Preprocess
            processed = self.preprocess_image(image)
            
            # Detect emotions
            results = self.detector.detect_emotions(processed)
            
            if not results or len(results) == 0:
                return None
            
            # Get first face
            emotion_scores = results[0]['emotions']
            
            return emotion_scores
            
        except Exception as e:
            print(f"⚠️ Detection error: {e}")
            return None
    
    def detect_emotion(self, image, use_ensemble=True):
        """
        Main detection dengan optional ensemble
        use_ensemble=True: lebih stabil tapi lebih lambat
        use_ensemble=False: lebih cepat
        """
        try:
            print(f"🎭 Detecting emotion...")
            
            if use_ensemble:
                # Ensemble: multiple detections dengan variasi
                all_scores = []
                
                # 1. Original image
                scores1 = self.detect_emotion_single(image)
                if scores1:
                    all_scores.append(scores1)
                
                # 2. Enhanced image
                enhanced = self.preprocess_image(image)
                scores2 = self.detect_emotion_single(enhanced)
                if scores2:
                    all_scores.append(scores2)
                
                # 3. Slightly brightened
                brightened = cv2.convertScaleAbs(image, alpha=1.1, beta=10)
                scores3 = self.detect_emotion_single(brightened)
                if scores3:
                    all_scores.append(scores3)
                
                if len(all_scores) == 0:
                    return 'neutral', 60.0, '😐', 'Netral'
                
                # Average scores
                avg_scores = {}
                for emotion in all_scores[0].keys():
                    avg_scores[emotion] = np.mean([s[emotion] for s in all_scores]) * 100
                
                emotion_scores = avg_scores
                
            else:
                # Single detection (faster)
                emotion_scores = self.detect_emotion_single(image)
                
                if not emotion_scores:
                    return 'neutral', 60.0, '😐', 'Netral'
                
                # Convert to percentage
                emotion_scores = {k: v * 100 for k, v in emotion_scores.items()}
            
            print(f"📊 FER 7-emotion scores:")
            for emotion, score in sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"   {emotion:12} {score:6.2f}%")
            
            # Map to 3 categories
            category_scores = {
                'positive': 0.0,
                'neutral': 0.0,
                'negative': 0.0
            }
            
            for emotion_7, score in emotion_scores.items():
                category = self.emotions_map[emotion_7]
                
                # WEIGHTED MAPPING
                if emotion_7 == 'happy':
                    category_scores['positive'] += score * 1.3  # Boost happy
                elif emotion_7 == 'surprise':
                    category_scores['positive'] += score * 0.8  # Partial positive
                    category_scores['neutral'] += score * 0.2
                else:
                    category_scores[category] += score
            
            # Normalize
            total = sum(category_scores.values())
            if total > 0:
                for key in category_scores:
                    category_scores[key] = (category_scores[key] / total) * 100
            
            print(f"\n📊 3-category scores:")
            for cat, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
                emoji = self.emotion_emoji[cat]
                indo = self.emotion_indonesian[cat]
                print(f"   {emoji} {cat:12} {score:6.2f}% ({indo})")
            
            # Get dominant
            dominant = max(category_scores, key=category_scores.get)
            raw_confidence = category_scores[dominant]
            
            # CONFIDENCE CALIBRATION
            # Masalah: FER sering overconfident atau underconfident
            # Solusi: Calibrate confidence berdasarkan range
            
            calibrated_confidence = self.calibrate_confidence(
                dominant, 
                raw_confidence, 
                category_scores
            )
            
            # SMART RULES
            positive_score = category_scores['positive']
            neutral_score = category_scores['neutral']
            negative_score = category_scores['negative']
            
            # Rule 1: Strong positive signal
            if positive_score > 35:
                dominant = 'positive'
                calibrated_confidence = min(90, 60 + (positive_score - 35))
                print(f"   ✅ Rule 1: Strong positive ({positive_score:.1f}%)")
            
            # Rule 2: Happy + Surprise combined
            happy_surprise = emotion_scores.get('happy', 0) + emotion_scores.get('surprise', 0)
            if happy_surprise > 25:
                dominant = 'positive'
                calibrated_confidence = min(88, 55 + (happy_surprise - 25))
                print(f"   ✅ Rule 2: Happy+Surprise ({happy_surprise:.1f}%)")
            
            # Rule 3: Very low confidence -> neutral
            if calibrated_confidence < 45:
                if positive_score > 20:
                    dominant = 'positive'
                    calibrated_confidence = 65
                    print(f"   ✅ Rule 3: Low conf but positive signal")
                else:
                    dominant = 'neutral'
                    calibrated_confidence = max(60, calibrated_confidence)
                    print(f"   ⚠️ Rule 3: Low confidence -> neutral")
            
            # Rule 4: Neutral dominant but positive close
            if dominant == 'neutral' and positive_score > neutral_score * 0.7:
                if positive_score > 25:
                    dominant = 'positive'
                    calibrated_confidence = 70
                    print(f"   ✅ Rule 4: Neutral vs Positive -> Positive")
            
            emoji = self.emotion_emoji[dominant]
            indonesian = self.emotion_indonesian[dominant]
            
            print(f"\n✅ Final: {emoji} {dominant.upper()} ({indonesian})")
            print(f"   Raw confidence: {raw_confidence:.1f}%")
            print(f"   Calibrated: {calibrated_confidence:.1f}%\n")
            
            return dominant, calibrated_confidence, emoji, indonesian
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            import traceback
            traceback.print_exc()
            return 'neutral', 65.0, '😐', 'Netral'
    
    def calibrate_confidence(self, emotion, raw_conf, all_scores):
        """
        Calibrate confidence untuk hasil lebih realistic
        
        Masalah umum:
        - FER sering output 99% padahal tidak yakin
        - Atau 30% padahal sebenarnya yakin
        
        Solusi: Calibration berdasarkan:
        1. Gap dengan emotion kedua
        2. Absolute score
        3. Emotion type
        """
        
        # Get second highest score
        sorted_scores = sorted(all_scores.values(), reverse=True)
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0
        
        # Calculate margin (gap antara 1st dan 2nd)
        margin = raw_conf - second_score
        
        # Base calibration
        if margin > 40:
            # Very confident (big gap)
            calibrated = min(92, 70 + (margin - 40) * 0.5)
        elif margin > 25:
            # Confident (medium gap)
            calibrated = min(85, 60 + (margin - 25) * 0.6)
        elif margin > 15:
            # Moderate confidence (small gap)
            calibrated = min(75, 55 + (margin - 15) * 0.8)
        else:
            # Low confidence (very small gap)
            calibrated = min(65, 50 + margin)
        
        # Adjust based on absolute score
        if raw_conf > 60:
            calibrated += 5
        elif raw_conf < 40:
            calibrated -= 5
        
        # Adjust based on emotion type
        if emotion == 'positive':
            # Slightly boost positive (optimistic bias)
            calibrated += 3
        elif emotion == 'negative':
            # Slightly reduce negative (avoid false negatives)
            calibrated -= 2
        
        # Clamp to range [50, 95]
        calibrated = max(50, min(95, calibrated))
        
        return calibrated
    
    def get_emotion_color(self, emotion):
        """Get color for emotion"""
        return self.emotion_color.get(emotion, '#6b7280')


# Export
class EmotionDetector(EmotionDetectorFER):
    """Alias untuk backward compatibility"""
    pass