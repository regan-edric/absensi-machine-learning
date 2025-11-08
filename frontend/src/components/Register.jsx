import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Camera from "./Camera";
import { registerUser, checkNIM, getUsers, deleteUser } from "../services/api";
import toast from "react-hot-toast";

const Register = () => {
  const navigate = useNavigate();
  const [registeredUsers, setRegisteredUsers] = useState([]);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ nama: "", nim: "" });
  const [capturedImages, setCapturedImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);

  const MIN_PHOTOS = 10;

  useEffect(() => {
    fetchRegisteredUsers();
  }, []);

  const fetchRegisteredUsers = async () => {
    try {
      const result = await getUsers();
      setRegisteredUsers(result.users || []);
    } catch (error) {
      console.error("Failed to fetch users:", error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleNextStep = async () => {
    if (!formData.nama || !formData.nim) {
      toast.error("Nama dan NIM harus diisi");
      return;
    }

    try {
      setIsLoading(true);
      const result = await checkNIM(formData.nim);

      if (result.exists) {
        toast.error("NIM sudah terdaftar");
        return;
      }

      setStep(2);
      setShowCamera(true);
    } catch (error) {
      toast.error("Gagal memeriksa NIM: ", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCapture = (imageSrc) => {
    setCapturedImages([...capturedImages, imageSrc]);
    toast.success(`Foto ${capturedImages.length + 1} berhasil diambil`);
  };

  const handleRemoveImage = (index) => {
    setCapturedImages(capturedImages.filter((_, i) => i !== index));
    toast.success("Foto dihapus");
  };

  const handleSubmit = async () => {
    if (capturedImages.length < MIN_PHOTOS) {
      toast.error(`Minimal ${MIN_PHOTOS} foto diperlukan`);
      return;
    }

    try {
      setIsLoading(true);
      await registerUser(formData.nama, formData.nim, capturedImages);

      toast.success("Registrasi berhasil!");

      setFormData({ nama: "", nim: "" });
      setCapturedImages([]);
      setStep(1);
      setShowCamera(false);
      fetchRegisteredUsers();
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || "Gagal melakukan registrasi";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setStep(1);
    setShowCamera(false);
    setCapturedImages([]);
  };

  const handleDeleteUser = async (userId, userName) => {
    if (!window.confirm(`Yakin ingin menghapus ${userName}?`)) {
      return;
    }

    try {
      setIsLoading(true);
      await deleteUser(userId);
      toast.success(`${userName} berhasil dihapus`);
      fetchRegisteredUsers();
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || "Gagal menghapus user";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <button
            onClick={() => navigate("/")}
            className="inline-flex items-center text-green-600 hover:text-green-700 font-medium mb-3 transition-colors"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Kembali ke Home
          </button>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
            Registrasi Mahasiswa
          </h1>
          <p className="text-gray-600 text-sm md:text-base">
            Daftarkan data dan wajah Anda ke dalam sistem
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left: Registered Users List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-5 sticky top-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <svg
                  className="w-5 h-5 mr-2 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
                Pengguna Terdaftar
              </h3>

              <div className="space-y-2 max-h-80 overflow-y-auto custom-scrollbar">
                {registeredUsers.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <svg
                      className="w-12 h-12 mx-auto mb-2 opacity-50"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                      />
                    </svg>
                    <p className="text-xs">Belum ada pengguna</p>
                  </div>
                ) : (
                  registeredUsers.map((user) => (
                    <div
                      key={user.id}
                      className="flex items-center p-2.5 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                    >
                      <div className="w-9 h-9 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold mr-2.5 text-sm flex-shrink-0">
                        {user.nama.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-gray-800 truncate">
                          {user.nama}
                        </p>
                        <p className="text-xs text-gray-500">{user.nim}</p>
                      </div>
                      <button
                        onClick={() => handleDeleteUser(user.id, user.nama)}
                        disabled={isLoading}
                        className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 p-1.5 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white rounded-md"
                        title="Hapus user"
                      >
                        <svg
                          className="w-3 h-3"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  ))
                )}
              </div>

              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-600 text-center">
                  Total:{" "}
                  <span className="font-bold text-green-600">
                    {registeredUsers.length}
                  </span>{" "}
                  pengguna
                </p>
              </div>
            </div>
          </div>

          {/* Right: Registration Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6 md:p-8">
              {/* Step 1: Form */}
              {step === 1 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-center mb-8">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                        1
                      </div>
                      <div className="w-20 h-1 bg-gray-300"></div>
                      <div className="w-10 h-10 bg-gray-300 text-white rounded-full flex items-center justify-center font-bold">
                        2
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Nama Lengkap *
                    </label>
                    <input
                      type="text"
                      name="nama"
                      value={formData.nama}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                      placeholder="Masukkan nama lengkap"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      NIM (Nomor Induk Mahasiswa) *
                    </label>
                    <input
                      type="text"
                      name="nim"
                      value={formData.nim}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                      placeholder="Masukkan NIM"
                    />
                  </div>

                  <button
                    onClick={handleNextStep}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    {isLoading ? "Memproses..." : "Lanjut ke Scan Wajah"}
                  </button>
                </div>
              )}

              {/* Step 2: Camera */}
              {step === 2 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between mb-6">
                    <button
                      onClick={handleBack}
                      className="flex items-center text-green-600 hover:text-green-700 font-medium"
                    >
                      <svg
                        className="w-5 h-5 mr-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 19l-7-7 7-7"
                        />
                      </svg>
                      Kembali
                    </button>

                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        ✓
                      </div>
                      <div className="w-16 h-1 bg-green-600"></div>
                      <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        2
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-4 mb-6">
                    <div className="flex items-start">
                      <svg
                        className="w-6 h-6 text-blue-500 mr-3 flex-shrink-0 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <div>
                        <p className="font-semibold text-blue-900 mb-1">
                          Tips Foto untuk Akurasi Maksimal:
                        </p>
                        <ul className="text-sm text-blue-800 space-y-1">
                          <li>
                            • <strong>Pencahayaan:</strong> Pastikan wajah
                            terang dan merata
                          </li>
                          <li>
                            • <strong>Posisi:</strong> Wajah menghadap kamera
                            langsung
                          </li>
                          <li>
                            • <strong>Jarak:</strong> 30-50cm dari kamera (tidak
                            terlalu dekat/jauh)
                          </li>
                          <li>
                            • <strong>Variasi:</strong> Ambil dari sudut sedikit
                            berbeda (kiri, depan, kanan)
                          </li>
                          <li>
                            • <strong>Ekspresi:</strong> Netral dan natural
                          </li>
                          <li>
                            • <strong>Minimal:</strong> {MIN_PHOTOS} foto
                            berbeda untuk hasil terbaik
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800">
                        Scan Wajah
                      </h3>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          capturedImages.length >= MIN_PHOTOS
                            ? "bg-green-100 text-green-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {capturedImages.length} / {MIN_PHOTOS} foto
                      </span>
                    </div>

                    {showCamera && (
                      <Camera onCapture={handleCapture} countdown={3} />
                    )}
                  </div>

                  {capturedImages.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">
                        Foto Terkumpul
                      </h3>
                      <div className="grid grid-cols-3 gap-4">
                        {capturedImages.map((img, index) => (
                          <div key={index} className="relative group">
                            <img
                              src={img}
                              alt={`Capture ${index + 1}`}
                              className="w-full h-32 object-cover rounded-lg shadow-md"
                            />
                            <button
                              onClick={() => handleRemoveImage(index)}
                              className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-7 h-7 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                            >
                              ×
                            </button>
                            <div className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
                              #{index + 1}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    onClick={handleSubmit}
                    disabled={capturedImages.length < MIN_PHOTOS || isLoading}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center">
                        <svg
                          className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        Memproses...
                      </span>
                    ) : (
                      `Simpan & Daftar (${capturedImages.length}/${MIN_PHOTOS})`
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
