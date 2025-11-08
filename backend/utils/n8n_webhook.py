import requests
from config import Config
from datetime import datetime

class N8NWebhook:
    def __init__(self):
        self.webhook_url = Config.N8N_WEBHOOK_URL
    
    def send_attendance_notification(self, user_data, attendance_data):
        """Send attendance notification to n8n webhook"""
        
        # Skip if webhook URL is default/not configured
        if not self.webhook_url or 'your-n8n-instance' in self.webhook_url:
            print("⚠️ N8N webhook not configured, skipping notification")
            return True, "N8N webhook not configured (skipped)"
        
        try:
            payload = {
                "nama": user_data['nama'],
                "nim": user_data['nim'],
                "timestamp": attendance_data['timestamp'].isoformat() if isinstance(attendance_data['timestamp'], datetime) else str(attendance_data['timestamp']),
                "status": attendance_data['status'],
                "confidence_score": float(attendance_data['confidence_score']),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5 
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully sent notification for {user_data['nama']}")
                return True, "Notifikasi berhasil dikirim"
            else:
                print(f"⚠️ Failed to send notification: {response.status_code}")
                return False, f"Gagal mengirim notifikasi: {response.status_code}"
                
        except requests.exceptions.Timeout:
            print("⚠️ Webhook request timeout")
            return False, "Timeout mengirim notifikasi (data tetap tersimpan)"
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Webhook request error: {e}")
            return False, f"Error mengirim notifikasi: {str(e)}"
        except Exception as e:
            print(f"⚠️ Unexpected error sending webhook: {e}")
            return False, f"Error tidak terduga: {str(e)}"
    
    def test_connection(self):
        """Test n8n webhook connection"""
        try:
            test_payload = {
                "test": True,
                "message": "Testing n8n webhook connection",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=5
            )
            
            return response.status_code == 200
        except:
            return False