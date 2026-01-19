import requests
from config import Config
from datetime import datetime
import logging
from threading import Thread
import time

logger = logging.getLogger(__name__)

class N8NWebhook:
    def __init__(self):
        self.webhook_url = Config.N8N_WEBHOOK_URL
        # INCREASED TIMEOUT untuk WhatsApp API
        self.timeout = Config.WEBHOOK_TIMEOUT if hasattr(Config, 'WEBHOOK_TIMEOUT') else 15
    
    def send_attendance_notification(self, user_data, attendance_data):
        """
        Send attendance notification to n8n webhook
        ASYNC VERSION - Tidak block response attendance
        """
        
        # Skip if webhook URL is default/not configured
        if not self.webhook_url or 'your-n8n-instance' in self.webhook_url:
            logger.warning("⚠️ N8N webhook not configured, skipping notification")
            return True, "N8N webhook not configured (skipped)"
        
        # OPTION 1: ASYNC (Recommended) - Tidak tunggu response
        # Kirim di background thread supaya tidak block attendance response
        thread = Thread(
            target=self._send_async,
            args=(user_data, attendance_data),
            daemon=True
        )
        thread.start()
        
        return True, "Notifikasi sedang dikirim (background)"
    
    def _send_async(self, user_data, attendance_data):
        """Send webhook in background thread"""
        try:
            payload = self._build_payload(user_data, attendance_data)
            
            logger.info(f"📤 Sending webhook to: {self.webhook_url}")
            logger.debug(f"📦 Payload: {payload}")
            
            start_time = time.time()
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'FaceAttendance/1.0'
                }
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                logger.info(f"✅ Webhook sent successfully in {elapsed:.2f}s for {user_data['nama']}")
                try:
                    response_data = response.json()
                    logger.debug(f"📥 Response: {response_data}")
                except:
                    logger.debug(f"📥 Response (text): {response.text}")
            else:
                logger.error(f"❌ Webhook failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Webhook timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Connection error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}", exc_info=True)
    
    def send_attendance_notification_sync(self, user_data, attendance_data):
        """
        SYNC VERSION - Tunggu response (untuk testing)
        Tidak direkomendasikan untuk production
        """
        
        if not self.webhook_url or 'your-n8n-instance' in self.webhook_url:
            logger.warning("⚠️ N8N webhook not configured")
            return True, "N8N webhook not configured (skipped)"
        
        try:
            payload = self._build_payload(user_data, attendance_data)
            
            logger.info(f"📤 Sending webhook SYNC to: {self.webhook_url}")
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Webhook sent for {user_data['nama']}")
                return True, "Notifikasi berhasil dikirim"
            else:
                logger.error(f"❌ Webhook failed: {response.status_code}")
                return False, f"Gagal: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Webhook timeout after {self.timeout}s")
            return False, f"Timeout ({self.timeout}s) - data tetap tersimpan"
        except requests.exceptions.ConnectionError:
            logger.error("🔌 Connection error - check if n8n is running")
            return False, "Tidak dapat terhubung ke n8n"
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            return False, f"Error: {str(e)}"
    
    def _build_payload(self, user_data, attendance_data):
        """Build webhook payload"""
        # Extract emotion data if available
        emotion_data = {}
        if 'emotion' in attendance_data:
            emotion_data = {
                'emotion': attendance_data['emotion'],
                'emotion_confidence': attendance_data.get('emotion_confidence', 0),
                'emoji': attendance_data.get('emoji', '😐')
            }
        
        return {
            "nama": user_data['nama'],
            "nim": user_data['nim'],
            "timestamp": attendance_data['timestamp'].isoformat() 
                if isinstance(attendance_data['timestamp'], datetime) 
                else str(attendance_data['timestamp']),
            "status": attendance_data['status'],
            "confidence_score": float(attendance_data['confidence_score']),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            **emotion_data  # Include emotion if available
        }
    
    def test_connection(self):
        """Test n8n webhook connection"""
        if not self.webhook_url or 'your-n8n-instance' in self.webhook_url:
            logger.error("❌ N8N webhook URL not configured")
            return False, "URL not configured"
        
        try:
            test_payload = {
                "test": True,
                "message": "Testing n8n webhook connection",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🧪 Testing webhook: {self.webhook_url}")
            
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=10  # Longer timeout for testing
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Webhook test successful: {response.status_code}")
                return True, "Connection OK"
            else:
                logger.error(f"❌ Test failed: {response.status_code}")
                return False, f"Failed: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("⏰ Test timeout")
            return False, "Timeout"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Connection error: {e}")
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            logger.error(f"💥 Test error: {e}")
            return False, f"Error: {str(e)}"