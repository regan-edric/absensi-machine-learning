import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'face_attendance_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Face Recognition Configuration
    # CHANGED: Tolerance sedikit lebih tinggi karena menggunakan minimum distance
    FACE_RECOGNITION_TOLERANCE = float(os.getenv('FACE_RECOGNITION_TOLERANCE', '0.45'))  # Was 0.6
    
    # CHANGED: Reduced dari 10 ke 5 untuk registrasi lebih cepat
    MIN_FACE_ENCODINGS = int(os.getenv('MIN_FACE_ENCODINGS', '5'))  # Was 10
    
    # NEW: Face encoding optimization
    # num_jitters untuk face encoding (1=fast, 5=accurate, 10=very accurate but slow)
    FACE_NUM_JITTERS = int(os.getenv('FACE_NUM_JITTERS', '1'))  # 1 = 5x faster
    
    # NEW: Face detection model ('hog'=fast, 'cnn'=accurate but needs GPU)
    FACE_DETECTION_MODEL = os.getenv('FACE_DETECTION_MODEL', 'hog')  # hog = 10x faster
    
    # NEW: Max image size for processing (auto-resize if larger)
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', '800'))  # pixels
    
    # Emotion Detection Configuration
    # CHANGED: Use simple detector by default (much faster)
    EMOTION_DETECTOR_TYPE = os.getenv('EMOTION_DETECTOR_TYPE', 'simple')  # 'simple' or 'deepface'
    
    # CHANGED: Lower threshold untuk senyum tipis
    EMOTION_CONFIDENCE_THRESHOLD = float(os.getenv('EMOTION_CONFIDENCE_THRESHOLD', '25'))  # Was 40
    
    # NEW: Smile detection threshold for MAR (Mouth Aspect Ratio)
    SMILE_MAR_THRESHOLD = float(os.getenv('SMILE_MAR_THRESHOLD', '0.25'))  # Lower = more sensitive
    
    # DEPRECATED: Tidak dipakai lagi dengan simple detector
    EMOTION_USE_MULTI_MODEL = os.getenv('EMOTION_USE_MULTI_MODEL', 'False').lower() == 'true'
    
    # N8N Webhook Configuration
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://your-n8n-instance.com/webhook/attendance')
    
    # NEW: Webhook timeout (seconds)
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', '15'))
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # NEW: Performance settings
    # Enable parallel processing for face encoding
    ENABLE_PARALLEL_PROCESSING = os.getenv('ENABLE_PARALLEL_PROCESSING', 'True').lower() == 'true'
    
    # Max worker threads for parallel processing
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # NEW: Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # 'simple' or 'redis'
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))  # 5 minutes
    
    # NEW: Rate limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')  # or redis://localhost:6379
    
    @staticmethod
    def get_db_connection_string():
        return f"host={Config.DB_HOST} port={Config.DB_PORT} dbname={Config.DB_NAME} user={Config.DB_USER} password={Config.DB_PASSWORD}"
    
    @staticmethod
    def get_config_summary():
        """Print current configuration for debugging"""
        return f"""╔══════════════════════════════════════════════════════════════╗
║                  CONFIGURATION SUMMARY                        ║
╠══════════════════════════════════════════════════════════════╣
║ Database:                                                     ║
║   Host: {Config.DB_HOST}:{Config.DB_PORT}                    
║   Database: {Config.DB_NAME}                                 
║                                                               ║
║ Face Recognition:                                             ║
║   Tolerance: {Config.FACE_RECOGNITION_TOLERANCE}             
║   Min Encodings: {Config.MIN_FACE_ENCODINGS}                 
║   Num Jitters: {Config.FACE_NUM_JITTERS}                     
║   Detection Model: {Config.FACE_DETECTION_MODEL}             
║   Max Image Size: {Config.MAX_IMAGE_SIZE}px                  
║                                                               ║
║ Emotion Detection:                                            ║
║   Type: {Config.EMOTION_DETECTOR_TYPE}                       
║   Confidence Threshold: {Config.EMOTION_CONFIDENCE_THRESHOLD}%
║   Smile MAR Threshold: {Config.SMILE_MAR_THRESHOLD}          
║                                                               ║
║ Performance:                                                  ║
║   Parallel Processing: {Config.ENABLE_PARALLEL_PROCESSING}   
║   Max Workers: {Config.MAX_WORKERS}                          
║   Cache Type: {Config.CACHE_TYPE}                            
║   Cache Timeout: {Config.CACHE_DEFAULT_TIMEOUT}s             
║                                                               ║
║ Flask:                                                        ║
║   Debug Mode: {Config.DEBUG}                                 
║   Rate Limiting: {Config.RATELIMIT_ENABLED}                  
╚══════════════════════════════════════════════════════════════╝
        """