-- Database: face_attendance_db

-- Drop tables if exists (untuk development)
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS face_encodings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    nim VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: face_encodings
CREATE TABLE face_encodings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    encoding BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: attendance
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score FLOAT,
    status VARCHAR(20) DEFAULT 'hadir',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_users_nim ON users(nim);
CREATE INDEX idx_face_encodings_user_id ON face_encodings(user_id);
CREATE INDEX idx_attendance_user_id ON attendance(user_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);