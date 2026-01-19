import face_recognition
import numpy as np
import cv2
from PIL import Image
import io
import base64
from config import Config

class FaceRecognitionHandler:
    def __init__(self):
        # OPTIMIZED: Lebih tinggi = lebih strict, lebih rendah = lebih lenient
        # 0.5-0.6 = optimal untuk most cases
        self.tolerance = 0.55  # Lebih balance
        
    def base64_to_image(self, base64_string):
        """Convert base64 string to numpy array image"""
        try:
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            image_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize jika terlalu besar (speed optimization)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.LANCZOS)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            img_array = np.array(image)
            return img_array
            
        except Exception as e:
            print(f"❌ Error converting base64: {e}")
            return None
    
    def enhance_image_quality(self, image):
        """Enhance image untuk face detection lebih baik"""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # CLAHE untuk contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced_gray = clahe.apply(gray)
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
            
            return enhanced
        except:
            return image
    
    def detect_face(self, image):
        """Detect face dengan preprocessing"""
        try:
            # Try dengan image asli dulu
            face_locations = face_recognition.face_locations(image, model='hog')
            
            # Jika gagal, coba dengan enhanced image
            if len(face_locations) == 0:
                enhanced = self.enhance_image_quality(image)
                face_locations = face_recognition.face_locations(enhanced, model='hog')
            
            if len(face_locations) == 0:
                return None, "Tidak ada wajah terdeteksi. Pastikan wajah terlihat jelas."
            
            if len(face_locations) > 1:
                # Pilih wajah terbesar (paling dekat ke kamera)
                face_locations = sorted(
                    face_locations, 
                    key=lambda loc: (loc[2]-loc[0])*(loc[1]-loc[3]), 
                    reverse=True
                )
            
            return face_locations[0], None
            
        except Exception as e:
            print(f"❌ Error detecting face: {e}")
            return None, f"Error: {str(e)}"
    
    def encode_face(self, image, num_jitters=3):
        """
        Encode face dengan multiple jitters untuk akurasi lebih baik
        num_jitters: 1=fast, 3=balanced, 5=accurate
        """
        try:
            face_location, error = self.detect_face(image)
            
            if error:
                return None, error
            
            # OPTIMIZED: num_jitters=3 (balance speed & accuracy)
            encodings = face_recognition.face_encodings(
                image, 
                [face_location],
                num_jitters=num_jitters
            )
            
            if len(encodings) == 0:
                return None, "Gagal mengekstrak encoding wajah"
            
            return encodings[0], None
        except Exception as e:
            print(f"❌ Error encoding face: {e}")
            return None, f"Error: {str(e)}"
    
    def compare_faces(self, known_encodings, face_encoding):
        """
        OPTIMIZED: Compare dengan multiple metrics
        Returns: (match, user_data, confidence)
        """
        try:
            if not known_encodings or len(known_encodings) == 0:
                return False, None, 0.0
            
            # Group encodings by user
            user_scores = {}
            
            for enc_data in known_encodings:
                user_id = enc_data['user_id']
                
                if user_id not in user_scores:
                    user_scores[user_id] = {
                        'distances': [],
                        'user_data': enc_data
                    }
                
                # Calculate distance (lower = more similar)
                distance = face_recognition.face_distance(
                    [enc_data['encoding']], 
                    face_encoding
                )[0]
                
                user_scores[user_id]['distances'].append(distance)
            
            # Find best match using WEIGHTED scoring
            best_match = None
            best_score = -1
            best_distance = float('inf')
            
            for user_id, data in user_scores.items():
                distances = np.array(data['distances'])
                
                # OPTIMIZED SCORING:
                # 1. Min distance (best case)
                min_dist = np.min(distances)
                
                # 2. Average distance (consistency)
                avg_dist = np.mean(distances)
                
                # 3. Median distance (robust to outliers)
                median_dist = np.median(distances)
                
                # Weighted score (lower = better)
                # Min=50%, Avg=30%, Median=20%
                combined_dist = (min_dist * 0.5) + (avg_dist * 0.3) + (median_dist * 0.2)
                
                # Convert to confidence (0-100%)
                # Distance 0.0 = 100%, Distance 1.0 = 0%
                confidence = max(0, (1 - combined_dist) * 100)
                
                print(f"User {data['user_data']['nama']}:")
                print(f"  Min dist: {min_dist:.4f}")
                print(f"  Avg dist: {avg_dist:.4f}")
                print(f"  Median dist: {median_dist:.4f}")
                print(f"  Combined: {combined_dist:.4f}")
                print(f"  Confidence: {confidence:.1f}%")
                
                # Track best match
                if combined_dist < best_distance:
                    best_distance = combined_dist
                    best_score = confidence
                    best_match = data['user_data']
            
            # DECISION: Accept if distance <= tolerance
            if best_distance <= self.tolerance:
                # Boost confidence jika sangat yakin
                if best_distance < 0.35:
                    best_score = min(99, best_score + 10)
                
                print(f"\n✅ MATCH: {best_match['nama']}")
                print(f"   Distance: {best_distance:.4f} (tolerance: {self.tolerance})")
                print(f"   Confidence: {best_score:.1f}%\n")
                
                return True, best_match, best_score
            
            print(f"\n❌ NO MATCH")
            print(f"   Best distance: {best_distance:.4f} > {self.tolerance}")
            print(f"   Confidence: {best_score:.1f}%\n")
            
            return False, None, best_score
            
        except Exception as e:
            print(f"❌ Error comparing faces: {e}")
            return False, None, 0.0
    
    def process_multiple_images(self, base64_images):
        """Process multiple images dengan quality filtering"""
        encodings = []
        quality_scores = []
        
        print(f"\n{'='*60}")
        print(f"📸 Processing {len(base64_images)} images...")
        print(f"{'='*60}\n")
        
        for idx, base64_img in enumerate(base64_images):
            print(f"Image {idx + 1}/{len(base64_images)}...")
            
            image = self.base64_to_image(base64_img)
            if image is None:
                print(f"❌ Failed to convert")
                continue
            
            # Validate quality
            is_valid, error_msg = self.validate_image_quality(image)
            if not is_valid:
                print(f"❌ Quality check failed: {error_msg}")
                continue
            
            # Encode dengan num_jitters=3 untuk balance
            encoding, error = self.encode_face(image, num_jitters=3)
            
            if error:
                print(f"❌ {error}")
                continue
            
            # Calculate quality score (sharpness)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            encodings.append(encoding)
            quality_scores.append(sharpness)
            
            print(f"✅ Encoded (sharpness: {sharpness:.1f})")
        
        # Sort by quality dan ambil top N
        if len(encodings) > 10:
            # Ambil 10 terbaik
            sorted_indices = np.argsort(quality_scores)[::-1][:10]
            encodings = [encodings[i] for i in sorted_indices]
            print(f"\n📊 Selected top 10 best quality images")
        
        print(f"\n{'='*60}")
        print(f"✅ Total valid encodings: {len(encodings)}/{len(base64_images)}")
        print(f"{'='*60}\n")
        
        return encodings
    
    def validate_image_quality(self, image):
        """Validate image quality"""
        try:
            height, width = image.shape[:2]
            
            if width < 100 or height < 100:
                return False, f"Gambar terlalu kecil ({width}x{height})"
            
            # Check brightness (lebih permisif)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray)
            
            if brightness < 15:
                return False, "Gambar terlalu gelap"
            
            if brightness > 245:
                return False, "Gambar terlalu terang"
            
            # Check sharpness (blur detection)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var < 50:
                return False, "Gambar terlalu blur"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating: {str(e)}"