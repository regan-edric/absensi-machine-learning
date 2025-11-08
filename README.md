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

Anggota:

1. 221110891 - Regan Edric Onggatta
2. 221111448 - Calvin Winata
3. 221110951 - Kelvin Sunliyanto

Cara Installasi:

lakukan di Terminal VS Code di Folder Backend:

1. py -3.11 -m venv venv
2. venv\scripts\activate
3. pip install flask flask-cors psycopg2-binary dlib face-recognition face-recognition-models opencv-python numpy pillow python-dotenv requests cmake
4. python app.py

lakukan di Terminal VS Code di Folder FrontEnd:

1. npm install
2. npm run dev

lakukan di Terminal VS Code di luar Folder FrontEnd dan Backend:

1. Nn8n start
