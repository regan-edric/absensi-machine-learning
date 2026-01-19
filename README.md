Tugas Machine Learning

Aplikasi Deteksi Wajah untuk Absensi berbasis Website

Aplikasi ini dirancang untuk memudahkan pekerjaan dosen dalam absensi dan mencegah mahasiswa untuk titip absen

teknologi / tech stack yang digunakan: 
React -> Front End -> Javascript 
Flask -> Backend -> Python 
PostgreSQL -> Database 
N8N -> Webhook untuk Otomasi Whatsapp Message/Notification 
Fonnte -> Whatsapp API yang dipakai 
HOG (Histogram of Oritented Gradients) -> Model ML yang dipakai
FER -> Model DL untuk Emotion Detection

Anggota:
221110891 - Regan Edric Onggatta
221111448 - Calvin Winata
221110951 - Kelvin Sunliyanto

Cara Installasi:

lakukan di Terminal VS Code di Folder Backend:
py -3.11 -m venv venv
venv\scripts\activate
pip install flask flask-cors psycopg2-binary dlib face-recognition face-recognition-models opencv-python numpy pillow python-dotenv requests cmake
python app.py

lakukan di Terminal VS Code di Folder FrontEnd:
npm install
npm run dev

lakukan di Terminal VS Code di luar Folder FrontEnd dan Backend:
npm install n8n -g
n8n start

Link Onedrive: https://mikroskilacid-my.sharepoint.com/:f:/g/personal/221110891_students_mikroskil_ac_id/IgD6ghtPNHt1T5JmFMGfXLTCAWcNxNpWatdVnmHpxdYebxw?e=lBKtxK
Link Youtube: https://youtu.be/X2mZBmCBFig
