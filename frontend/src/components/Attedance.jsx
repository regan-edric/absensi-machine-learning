import React, { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Webcam from "react-webcam";
import { checkAttendance } from "../services/api";
import toast from "react-hot-toast";

const Attendance = () => {
  const navigate = useNavigate();
  const webcamRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isCameraReady, setIsCameraReady] = useState(false);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user",
  };

  const handleUserMedia = () => {
    setIsCameraReady(true);
  };

  const handleCheckAttendance = useCallback(async () => {
    if (!webcamRef.current) {
      toast.error("Kamera belum siap");
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const imageSrc = webcamRef.current.getScreenshot({
        width: 1280,
        height: 720,
      });

      if (!imageSrc) {
        toast.error("Gagal mengambil gambar");
        return;
      }

      const response = await checkAttendance(imageSrc);
      setResult(response);

      if (response.recognized && !response.already_recorded) {
        toast.success(`Selamat datang, ${response.user.nama}!`);
      } else if (response.already_recorded) {
        toast.error(response.message);
      } else {
        toast.error("Wajah tidak dikenali");
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || "Gagal melakukan pengecekan";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [webcamRef]);

  const handleReset = () => {
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-8">
      <div className="max-w-3xl w-full">
        {/* Header */}
        <div className="text-center mb-6">
          <button
            onClick={() => navigate("/")}
            className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium mb-3 transition-colors"
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
            Absensi
          </h1>
          <p className="text-gray-600 text-sm md:text-base">
            Scan wajah Anda untuk mencatat kehadiran
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
          {/* Camera Section */}
          <div className="relative bg-gray-900">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMedia={handleUserMedia}
              className="w-full h-auto"
            />

            {!isCameraReady && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                  <p className="text-white">Memuat kamera...</p>
                </div>
              </div>
            )}

            {/* Overlay Frame */}
            {isCameraReady && !result && (
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-80 h-96 border-4 border-blue-500 rounded-3xl shadow-2xl">
                    <div className="absolute -top-2 -left-2 w-8 h-8 border-t-4 border-l-4 border-blue-500 rounded-tl-lg"></div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 border-t-4 border-r-4 border-blue-500 rounded-tr-lg"></div>
                    <div className="absolute -bottom-2 -left-2 w-8 h-8 border-b-4 border-l-4 border-blue-500 rounded-bl-lg"></div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 border-b-4 border-r-4 border-blue-500 rounded-br-lg"></div>
                  </div>
                </div>
                <div className="absolute bottom-8 left-0 right-0 text-center">
                  <p className="text-white text-lg font-semibold bg-black/50 inline-block px-6 py-2 rounded-full">
                    Posisikan wajah Anda di dalam frame
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Content Section */}
          <div className="p-8">
            {!result ? (
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
                  <div className="flex items-start">
                    <svg
                      className="w-6 h-6 text-yellow-500 mr-3 flex-shrink-0 mt-0.5"
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
                      <p className="font-semibold text-yellow-900 mb-1">
                        Panduan Absensi:
                      </p>
                      <ul className="text-sm text-yellow-800 space-y-1">
                        <li>
                          • Pastikan wajah Anda terlihat jelas di dalam frame
                        </li>
                        <li>• Pencahayaan harus cukup dan merata</li>
                        <li>• Lepaskan masker atau kacamata hitam</li>
                        <li>• Klik tombol "Mulai Absensi" untuk memulai</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleCheckAttendance}
                  disabled={!isCameraReady || isLoading}
                  className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-3 h-6 w-6 text-white"
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
                    <span className="flex items-center justify-center">
                      <svg
                        className="w-6 h-6 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Mulai Absensi
                    </span>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Success Result */}
                {result.recognized && !result.already_recorded && (
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-500 rounded-2xl p-8">
                    <div className="flex items-center justify-center mb-6">
                      <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center shadow-lg animate-bounce">
                        <svg
                          className="w-10 h-10 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    </div>

                    <h3 className="text-3xl font-bold text-green-800 text-center mb-6">
                      Absensi Berhasil!
                    </h3>

                    <div className="bg-white rounded-xl p-6 space-y-4 shadow-md">
                      <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Nama</span>
                        <span className="text-gray-900 font-bold">
                          {result.user.nama}
                        </span>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">NIM</span>
                        <span className="text-gray-900 font-bold">
                          {result.user.nim}
                        </span>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">Waktu</span>
                        <span className="text-gray-900 font-bold">
                          {new Date(result.attendance.timestamp).toLocaleString(
                            "id-ID"
                          )}
                        </span>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <span className="text-gray-600 font-medium">
                          Status
                        </span>
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-bold text-sm">
                          {result.attendance.status}
                        </span>
                      </div>
                      <div className="flex items-center justify-between py-3">
                        <span className="text-gray-600 font-medium">
                          Confidence
                        </span>
                        <span className="text-gray-900 font-bold">
                          {(result.attendance.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    {result.notification && (
                      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center">
                          <svg
                            className="w-5 h-5 text-blue-600 mr-2"
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
                          <span className="text-sm text-blue-800">
                            {result.notification.sent
                              ? "✅ Notifikasi WhatsApp telah dikirim ke HRD"
                              : "⚠️ Gagal mengirim notifikasi WhatsApp"}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Already Recorded Result */}
                {result.already_recorded && (
                  <div className="bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-500 rounded-2xl p-8">
                    <div className="flex items-center justify-center mb-6">
                      <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-amber-600 rounded-full flex items-center justify-center shadow-lg">
                        <svg
                          className="w-10 h-10 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                          />
                        </svg>
                      </div>
                    </div>

                    <h3 className="text-3xl font-bold text-yellow-800 text-center mb-4">
                      Sudah Absen Hari Ini
                    </h3>
                    <p className="text-yellow-700 text-center mb-6">
                      {result.message}
                    </p>

                    <div className="bg-white rounded-xl p-6 space-y-3 shadow-md">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Nama</span>
                        <span className="text-gray-900 font-bold">
                          {result.user.nama}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">NIM</span>
                        <span className="text-gray-900 font-bold">
                          {result.user.nim}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Waktu Absen</span>
                        <span className="text-gray-900 font-bold">
                          {new Date(result.last_attendance).toLocaleString(
                            "id-ID"
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Not Recognized Result */}
                {!result.recognized && (
                  <div className="bg-gradient-to-br from-red-50 to-rose-50 border-2 border-red-500 rounded-2xl p-8">
                    <div className="flex items-center justify-center mb-6">
                      <div className="w-20 h-20 bg-gradient-to-br from-red-400 to-rose-600 rounded-full flex items-center justify-center shadow-lg">
                        <svg
                          className="w-10 h-10 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </div>
                    </div>

                    <h3 className="text-3xl font-bold text-red-800 text-center mb-4">
                      Wajah Tidak Dikenali
                    </h3>
                    <p className="text-red-700 text-center mb-6">
                      {result.message}
                    </p>

                    <div className="bg-white rounded-xl p-6 shadow-md">
                      <p className="text-gray-700 mb-4">
                        Kemungkinan penyebab:
                      </p>
                      <ul className="space-y-2 text-gray-600">
                        <li className="flex items-start">
                          <span className="text-red-500 mr-2">•</span>
                          <span>Anda belum terdaftar dalam sistem</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-red-500 mr-2">•</span>
                          <span>Pencahayaan kurang baik</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-red-500 mr-2">•</span>
                          <span>Wajah tidak terlihat jelas</span>
                        </li>
                      </ul>

                      <button
                        onClick={() => navigate("/register")}
                        className="w-full mt-6 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-all"
                      >
                        Daftar Sekarang
                      </button>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleReset}
                  className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg"
                >
                  Coba Lagi
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Attendance;
