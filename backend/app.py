from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import Database, UserModel, FaceEncodingModel, AttendanceModel
from utils.face_recognition import FaceRecognitionHandler
from utils.n8n_webhook import N8NWebhook
from utils.emotion_detector import EmotionDetector
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize handlers
face_handler = FaceRecognitionHandler()
n8n_webhook = N8NWebhook()
emotion_detector = EmotionDetector()

def get_db():
    db = Database()
    db.connect()
    return db

# ============= REGISTER ROUTES =============

@app.route('/api/register/check-nim', methods=['POST'])
def check_nim():
    """Check if NIM already exists"""
    try:
        data = request.get_json()
        nim = data.get('nim')
        
        if not nim:
            return jsonify({'error': 'NIM is required'}), 400
        
        db = get_db()
        user_model = UserModel(db)
        
        exists = user_model.check_nim_exists(nim)
        db.close()
        
        return jsonify({'exists': exists})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    """Register new user with face encodings"""
    try:
        data = request.get_json()
        nama = data.get('nama')
        nim = data.get('nim')
        images = data.get('images', [])
        
        if not nama or not nim:
            return jsonify({'error': 'Nama dan NIM harus diisi'}), 400
        
        if len(images) < Config.MIN_FACE_ENCODINGS:
            return jsonify({'error': f'Minimal {Config.MIN_FACE_ENCODINGS} foto diperlukan'}), 400
        
        db = get_db()
        user_model = UserModel(db)
        face_model = FaceEncodingModel(db)
        
        if user_model.check_nim_exists(nim):
            db.close()
            return jsonify({'error': 'NIM sudah terdaftar'}), 400
        
        encodings = face_handler.process_multiple_images(images)
        
        if len(encodings) < Config.MIN_FACE_ENCODINGS:
            db.close()
            return jsonify({
                'error': f'Hanya {len(encodings)} foto valid dari {len(images)}. Minimal {Config.MIN_FACE_ENCODINGS} foto diperlukan'
            }), 400
        
        user = user_model.create_user(nama, nim)
        
        if not user:
            db.close()
            return jsonify({'error': 'Gagal membuat user'}), 500
        
        for encoding in encodings:
            face_model.save_encoding(user['id'], encoding)
        
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Registrasi berhasil',
            'user': {
                'id': user['id'],
                'nama': user['nama'],
                'nim': user['nim'],
                'encodings_saved': len(encodings)
            }
        }), 201
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'error': str(e)}), 500

# ============= ATTENDANCE ROUTES =============

@app.route('/api/attendance/check', methods=['POST'])
def check_attendance():
    """Check attendance using face recognition + emotion detection"""
    try:
        data = request.get_json()
        image = data.get('image')
        
        if not image:
            return jsonify({'error': 'Image is required'}), 400
        
        # Convert base64 to image
        img_array = face_handler.base64_to_image(image)
        
        if img_array is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Validate image quality
        is_valid, error_msg = face_handler.validate_image_quality(img_array)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Extract face encoding
        face_encoding, error = face_handler.encode_face(img_array)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Detect emotion
        emotion, emotion_confidence, emoji, emotion_indonesian = emotion_detector.detect_emotion(img_array)
        emotion_color = emotion_detector.get_emotion_color(emotion)
        
        # Get all known encodings from database
        db = get_db()
        face_model = FaceEncodingModel(db)
        known_encodings = face_model.get_all_encodings()
        
        if not known_encodings:
            db.close()
            return jsonify({'error': 'Belum ada data wajah terdaftar'}), 404
        
        # Compare faces
        match, user_data, confidence = face_handler.compare_faces(known_encodings, face_encoding)
        
        if not match:
            db.close()
            return jsonify({
                'recognized': False,
                'message': 'Wajah tidak dikenali',
                'confidence': float(confidence),
                'emotion': {
                    'detected': emotion,
                    'indonesian': emotion_indonesian,
                    'emoji': emoji,
                    'confidence': float(emotion_confidence),
                    'color': emotion_color
                }
            }), 200
        
        # Check if already recorded today
        attendance_model = AttendanceModel(db)
        today_attendance = attendance_model.get_today_attendance(user_data['user_id'])
        
        if today_attendance and len(today_attendance) > 0:
            db.close()
            return jsonify({
                'recognized': True,
                'already_recorded': True,
                'message': f"{user_data['nama']} sudah absen hari ini",
                'user': {
                    'nama': user_data['nama'],
                    'nim': user_data['nim']
                },
                'last_attendance': today_attendance[0]['timestamp'].isoformat() if isinstance(today_attendance[0]['timestamp'], datetime) else str(today_attendance[0]['timestamp']),
                'emotion': {
                    'detected': emotion,
                    'indonesian': emotion_indonesian,
                    'emoji': emoji,
                    'confidence': float(emotion_confidence),
                    'color': emotion_color
                }
            }), 200
        
        # Record attendance WITH MOOD
        attendance_record = attendance_model.record_attendance(
            user_data['user_id'],
            float(confidence),
            'hadir',
            emotion,
            float(emotion_confidence),
            emoji
        )
        
        db.close()
        
        # Send notification to n8n
        n8n_success, n8n_message = n8n_webhook.send_attendance_notification(
            user_data,
            attendance_record
        )
        
        return jsonify({
            'recognized': True,
            'already_recorded': False,
            'message': f"Absensi berhasil dicatat untuk {user_data['nama']}",
            'user': {
                'nama': user_data['nama'],
                'nim': user_data['nim']
            },
            'attendance': {
                'timestamp': attendance_record['timestamp'].isoformat() if isinstance(attendance_record['timestamp'], datetime) else str(attendance_record['timestamp']),
                'confidence': float(confidence),
                'status': attendance_record['status']
            },
            'emotion': {
                'detected': emotion,
                'indonesian': emotion_indonesian,
                'emoji': emoji,
                'confidence': float(emotion_confidence),
                'color': emotion_color
            },
            'notification': {
                'sent': n8n_success,
                'message': n8n_message
            }
        }), 201
        
    except Exception as e:
        print(f"Attendance check error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============= UTILITY ROUTES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_db()
        db.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected'
        }), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users"""
    try:
        db = get_db()
        user_model = UserModel(db)
        
        query = "SELECT id, nama, nim, created_at FROM users ORDER BY created_at DESC"
        users = db.execute_query(query, fetch=True)
        
        db.close()
        
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user by ID"""
    try:
        db = get_db()
        user_model = UserModel(db)
        
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            db.close()
            return jsonify({'error': 'User tidak ditemukan'}), 404
        
        deleted = user_model.delete_user(user_id)
        
        db.close()
        
        if deleted:
            return jsonify({
                'success': True,
                'message': f"User {deleted['nama']} berhasil dihapus",
                'user': {
                    'id': deleted['id'],
                    'nama': deleted['nama'],
                    'nim': deleted['nim']
                }
            }), 200
        else:
            return jsonify({'error': 'Gagal menghapus user'}), 500
        
    except Exception as e:
        print(f"Delete user error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)