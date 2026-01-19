import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
import pickle
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                Config.get_db_connection_string(),
                cursor_factory=RealDictCursor
            )
            return self.connection
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Exception as e:
            self.connection.rollback()
            print(f"Query execution error: {e}")
            raise
    
    def commit(self):
        """Explicit commit"""
        try:
            self.connection.commit()
        except Exception as e:
            print(f"Commit error: {e}")
            raise

class UserModel:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, nama, nim):
        try:
            query = """
                INSERT INTO users (nama, nim) 
                VALUES (%s, %s) 
                RETURNING id, nama, nim, created_at
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query, (nama, nim))
            result = cursor.fetchone()
            self.db.connection.commit()
            cursor.close()
            
            if result:
                print(f"✅ User created successfully: ID={result['id']}, Nama={result['nama']}")
            
            return result if result else None
        except Exception as e:
            self.db.connection.rollback()
            print(f"❌ Error creating user: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_by_nim(self, nim):
        query = "SELECT * FROM users WHERE nim = %s"
        result = self.db.execute_query(query, (nim,), fetch=True)
        return result[0] if result else None
    
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_query(query, (user_id,), fetch=True)
        return result[0] if result else None
    
    def check_nim_exists(self, nim):
        query = "SELECT COUNT(*) as count FROM users WHERE nim = %s"
        result = self.db.execute_query(query, (nim,), fetch=True)
        return result[0]['count'] > 0
    
    def delete_user(self, user_id):
        """Delete user and all related data (CASCADE)"""
        try:
            query = "DELETE FROM users WHERE id = %s RETURNING id, nama, nim"
            cursor = self.db.connection.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            self.db.connection.commit()
            cursor.close()
            
            if result:
                print(f"✅ User deleted: {result['nama']} ({result['nim']})")
            
            return result if result else None
        except Exception as e:
            self.db.connection.rollback()
            print(f"❌ Error deleting user: {e}")
            import traceback
            traceback.print_exc()
            return None

class FaceEncodingModel:
    def __init__(self, db):
        self.db = db
    
    def save_encoding(self, user_id, encoding):
        try:
            encoding_bytes = pickle.dumps(encoding)
            query = """
                INSERT INTO face_encodings (user_id, encoding) 
                VALUES (%s, %s)
                RETURNING id
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query, (user_id, encoding_bytes))
            result = cursor.fetchone()
            self.db.connection.commit()
            cursor.close()
            
            if result:
                print(f"   ✅ Face encoding saved: ID={result['id']}, user_id={user_id}")
            
            return result if result else None
        except Exception as e:
            self.db.connection.rollback()
            print(f"   ❌ Error saving encoding: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_all_encodings(self):
        query = """
            SELECT fe.id, fe.user_id, fe.encoding, u.nama, u.nim
            FROM face_encodings fe
            JOIN users u ON fe.user_id = u.id
        """
        results = self.db.execute_query(query, fetch=True)
        
        for result in results:
            result['encoding'] = pickle.loads(result['encoding'])
        
        return results
    
    def get_encodings_by_user_id(self, user_id):
        query = "SELECT * FROM face_encodings WHERE user_id = %s"
        results = self.db.execute_query(query, (user_id,), fetch=True)
        
        for result in results:
            result['encoding'] = pickle.loads(result['encoding'])
        
        return results

class AttendanceModel:
    def __init__(self, db):
        self.db = db
    
    def record_attendance(self, user_id, confidence_score, status='hadir', mood=None, mood_confidence=None, mood_emoji=None):
        """Record attendance with mood tracking"""
        if hasattr(confidence_score, 'item'):
            confidence_score = confidence_score.item()
        else:
            confidence_score = float(confidence_score)
        
        if mood_confidence is not None:
            if hasattr(mood_confidence, 'item'):
                mood_confidence = mood_confidence.item()
            else:
                mood_confidence = float(mood_confidence)
        
        query = """
            INSERT INTO attendance (user_id, confidence_score, status, timestamp, mood, mood_confidence, mood_emoji)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, timestamp, confidence_score, status, mood, mood_confidence, mood_emoji
        """
        timestamp = datetime.now()
        result = self.db.execute_query(
            query, 
            (user_id, confidence_score, status, timestamp, mood, mood_confidence, mood_emoji), 
            fetch=True
        )
        return result[0] if result else None
    
    def get_today_attendance(self, user_id):
        query = """
            SELECT * FROM attendance 
            WHERE user_id = %s 
            AND DATE(timestamp) = CURRENT_DATE
            ORDER BY timestamp DESC
        """
        return self.db.execute_query(query, (user_id,), fetch=True)
    
    def get_all_attendance(self, limit=100):
        query = """
            SELECT a.*, u.nama, u.nim
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,), fetch=True)