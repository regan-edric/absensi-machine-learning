import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Register API
export const checkNIM = async (nim) => {
  const response = await api.post("/register/check-nim", { nim });
  return response.data;
};

export const registerUser = async (nama, nim, images) => {
  const response = await api.post("/register", { nama, nim, images });
  return response.data;
};

// Attendance API
export const checkAttendance = async (image) => {
  const response = await api.post("/attendance/check", { image });
  return response.data;
};

// Utility API
export const healthCheck = async () => {
  const response = await api.get("/health");
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get("/users");
  return response.data;
};

export const getAttendanceHistory = async (limit = 100) => {
  const response = await api.get(`/attendance/history?limit=${limit}`);
  return response.data;
};

// Delete User
export const deleteUser = async (userId) => {
  const response = await api.delete(`/users/${userId}`);
  return response.data;
};

export default api;
