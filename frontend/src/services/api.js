import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds for registration (processing images takes time)
  // IMPORTANT: Accept 2xx status codes
  validateStatus: function (status) {
    return status >= 200 && status < 300; // Accept 200-299 as success
  },
});

// Add request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method.toUpperCase()} ${config.url}`);

    // Add timestamp to GET requests to prevent caching
    if (config.method === "get") {
      config.params = {
        ...config.params,
        _: new Date().getTime(),
      };
    }
    return config;
  },
  (error) => {
    console.error("❌ Request interceptor error:", error);
    return Promise.reject(error);
  },
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    console.log("Response data:", response.data);
    return response;
  },
  (error) => {
    console.error("❌ API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    // Add more context to error
    if (error.response) {
      // Server responded with error status
      error.message =
        error.response.data?.error ||
        error.response.data?.message ||
        `Server error: ${error.response.status}`;
    } else if (error.request) {
      // Request made but no response
      error.message =
        "Tidak dapat terhubung ke server. Periksa koneksi internet Anda.";
    }

    return Promise.reject(error);
  },
);

// Register API
export const checkNIM = async (nim) => {
  try {
    console.log("🔍 Checking NIM:", nim);
    const response = await api.post("/register/check-nim", { nim });
    return response.data;
  } catch (error) {
    console.error("Check NIM error:", error);
    throw error;
  }
};

export const registerUser = async (nama, nim, images) => {
  try {
    console.log("📝 Registering user:", {
      nama,
      nim,
      imageCount: images.length,
    });

    const payload = {
      nama: nama.trim(),
      nim: nim.trim(),
      images,
    };

    const response = await api.post("/register", payload);

    console.log("✅ Registration successful:", response.data);

    // Return response data directly
    // Backend returns: { success: true, message: '...', data: {...} }
    return response.data;
  } catch (error) {
    console.error("❌ Registration error:", error);

    // Re-throw with additional context
    if (error.response?.status === 400) {
      console.error("Validation error:", error.response.data);
    } else if (error.response?.status === 500) {
      console.error("Server error:", error.response.data);
    }

    throw error;
  }
};

// Attendance API
export const checkAttendance = async (image) => {
  try {
    console.log("📸 Checking attendance...");
    const response = await api.post("/attendance/check", { image });
    return response.data;
  } catch (error) {
    console.error("Check attendance error:", error);
    throw error;
  }
};

// Utility API
export const healthCheck = async () => {
  try {
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    console.error("Health check error:", error);
    throw error;
  }
};

export const getUsers = async () => {
  try {
    console.log("👥 Fetching users...");
    const response = await api.get("/users");
    console.log("Users fetched:", response.data.users?.length || 0);
    return response.data;
  } catch (error) {
    console.error("Get users error:", error);
    throw error;
  }
};

export const getAttendanceHistory = async (limit = 100) => {
  try {
    const response = await api.get(`/attendance/history?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error("Get attendance history error:", error);
    throw error;
  }
};

export const deleteUser = async (userId) => {
  try {
    console.log("🗑️ Deleting user:", userId);
    const response = await api.delete(`/users/${userId}`);
    console.log("✅ User deleted:", response.data);
    return response.data;
  } catch (error) {
    console.error("Delete user error:", error);
    throw error;
  }
};

export default api;
