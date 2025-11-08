import face_recognition
import numpy as np
import cv2
from PIL import Image
import io
import base64
from config import Config

class FaceRecognitionHandler:
    def __init__(self):
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
    
    def base64_to_image(self, base64_string):
        """Convert base64 string to numpy array image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB (face_recognition requires RGB)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            print(f"✅ Image converted successfully: {img_array.shape}, dtype: {img_array.dtype}")
            
            return img_array
            
        except Exception as e:
            print(f"❌ Error converting base64 to image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def detect_face(self, image):
        """Detect face in image and return face location"""
        try:
            print(f"🔍 Detecting face in image shape: {image.shape}")
            
            face_locations = face_recognition.face_locations(image, model='hog')  # Use HOG model (faster)
            
            print(f"📍 Face locations found: {len(face_locations)}")
            
            if len(face_locations) == 0:
                return None, "Tidak ada wajah terdeteksi. Pastikan wajah terlihat jelas."
            
            if len(face_locations) > 1:
                print(f"⚠️ Multiple faces detected: {len(face_locations)}, using the first one")
                # Use the largest face
                face_locations = sorted(face_locations, key=lambda loc: (loc[2]-loc[0])*(loc[1]-loc[3]), reverse=True)
            
            return face_locations[0], None
            
        except Exception as e:
            print(f"❌ Error detecting face: {e}")
            import traceback
            traceback.print_exc()
            return None, f"Error: {str(e)}"
    
    def encode_face(self, image):
        try:
            face_location, error = self.detect_face(image)
            
            if error:
                return None, error
            
            # num_jitters=5 (balance: 5 is good, 10 is overkill)
            encodings = face_recognition.face_encodings(
                image, 
                [face_location],
                num_jitters=5
            )
            
            if len(encodings) == 0:
                return None, "Gagal mengekstrak encoding wajah"
            
            return encodings[0], None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None, f"Error: {str(e)}"
    
    def compare_faces(self, known_encodings, face_encoding):
        """
        Compare face encoding with known encodings
        Returns: (match, user_data, confidence)
        """
        try:
            if not known_encodings or len(known_encodings) == 0:
                return False, None, 0.0
            
            # Group encodings by user
            user_distances = {}
            
            for enc_data in known_encodings:
                user_id = enc_data['user_id']
                
                if user_id not in user_distances:
                    user_distances[user_id] = {
                        'distances': [],
                        'user_data': enc_data
                    }
                
                # Calculate distance
                distance = face_recognition.face_distance([enc_data['encoding']], face_encoding)[0]
                user_distances[user_id]['distances'].append(distance)
            
            # Find best match using AVERAGE of all encodings
            best_match = None
            best_avg_distance = float('inf')
            
            for user_id, data in user_distances.items():
                # Average distance (more reliable than single best)
                avg_distance = float(np.mean(data['distances']))
                
                if avg_distance < best_avg_distance:
                    best_avg_distance = avg_distance
                    best_match = data['user_data']
            
            # Convert to confidence
            confidence = float(1 - best_avg_distance)
            
            print(f"🎯 Best match: {best_match['nama'] if best_match else 'None'}")
            print(f"   Avg distance: {best_avg_distance:.4f}")
            print(f"   Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
            
            # Check threshold
            if best_avg_distance <= self.tolerance:
                return True, best_match, confidence
            
            return False, None, confidence
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, None, 0.0
    
    def process_multiple_images(self, base64_images):
        """Process multiple images and return all valid encodings"""
        encodings = []
        
        print(f"\n{'='*50}")
        print(f"🔄 Processing {len(base64_images)} images...")
        print(f"{'='*50}\n")
        
        for idx, base64_img in enumerate(base64_images):
            print(f"\n📸 Processing image {idx + 1}/{len(base64_images)}...")
            
            image = self.base64_to_image(base64_img)
            
            if image is None:
                print(f"❌ Image {idx + 1}: Failed to convert base64")
                continue
            
            # Validate image quality
            is_valid, error_msg = self.validate_image_quality(image)
            if not is_valid:
                print(f"❌ Image {idx + 1}: Quality check failed - {error_msg}")
                continue
            
            encoding, error = self.encode_face(image)
            
            if error:
                print(f"❌ Image {idx + 1}: {error}")
                continue
            
            encodings.append(encoding)
            print(f"✅ Image {idx + 1}: Successfully encoded!")
        
        print(f"\n{'='*50}")
        print(f"✅ Total valid encodings: {len(encodings)}/{len(base64_images)}")
        print(f"{'='*50}\n")
        
        return encodings
    
    def validate_image_quality(self, image):
        """Validate if image quality is good enough"""
        try:
            # Check image size
            height, width = image.shape[:2]
            
            print(f"   📏 Image size: {width}x{height}")
            
            if width < 100 or height < 100:
                return False, f"Gambar terlalu kecil ({width}x{height})"
            
            # Check brightness (make it more permissive)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray)
            
            print(f"   💡 Brightness: {brightness:.1f}")
            
            if brightness < 20:
                return False, "Gambar terlalu gelap"
            
            if brightness > 240:
                return False, "Gambar terlalu terang"
            
            return True, None
            
        except Exception as e:
            print(f"   ❌ Validation error: {str(e)}")
            return False, f"Error validating image: {str(e)}"