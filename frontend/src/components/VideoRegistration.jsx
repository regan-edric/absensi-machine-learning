import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
// import { registerUser, checkNIM } from "../services/api";
import toast from "react-hot-toast";

const VideoRegistration = ({ onComplete }) => {
  const webcamRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const [capturedFrames, setCapturedFrames] = useState([]);
  const [currentInstruction, setCurrentInstruction] = useState("center");
  const [progress, setProgress] = useState(0);
  const intervalRef = useRef(null);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user",
    // deviceId: {
    //   exact: "2c65ba64799d47172376520d16dd51083830365f708105ff115ffbdeb55f03c9",
    // },
    // frameRate: { ideal: 30 },
  };

  const instructions = [
    { position: "center", text: "Lihat ke depan", duration: 1000 },
    { position: "left", text: "Lihat ke kiri", duration: 800 },
    { position: "center", text: "Lihat ke depan", duration: 800 },
    { position: "right", text: "Lihat ke kanan", duration: 800 },
    { position: "center", text: "Lihat ke depan", duration: 800 },
    { position: "up", text: "Lihat ke atas", duration: 800 },
    { position: "down", text: "Lihat ke bawah", duration: 800 },
    { position: "center", text: "Selesai!", duration: 500 },
  ];

  const startRecording = () => {
    setCountdown(3);
    const countdownInterval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownInterval);
          startCapturing();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const startCapturing = () => {
    setIsRecording(true);
    setCapturedFrames([]);
    setProgress(0);

    let currentStep = 0;
    let frames = [];

    const captureFrame = () => {
      if (!webcamRef.current) return;

      const imageSrc = webcamRef.current.getScreenshot({
        width: 1280,
        height: 720,
      });

      if (imageSrc) {
        frames.push(imageSrc);
      }
    };

    // Capture frames based on instructions
    let stepStartTime = Date.now();

    intervalRef.current = setInterval(() => {
      const elapsed = Date.now() - stepStartTime;
      const currentInstr = instructions[currentStep];

      // Capture frame every 200ms during instruction
      if (elapsed % 200 < 50) {
        captureFrame();
      }

      // Update progress
      const totalDuration = instructions.reduce(
        (sum, i) => sum + i.duration,
        0
      );
      const progressSoFar =
        instructions
          .slice(0, currentStep)
          .reduce((sum, i) => sum + i.duration, 0) + elapsed;
      setProgress((progressSoFar / totalDuration) * 100);

      // Move to next instruction
      if (elapsed >= currentInstr.duration) {
        currentStep++;
        stepStartTime = Date.now();

        if (currentStep >= instructions.length) {
          clearInterval(intervalRef.current);
          finishCapturing(frames);
        } else {
          setCurrentInstruction(instructions[currentStep].position);
        }
      }
    }, 50);
  };

  const finishCapturing = (frames) => {
    setIsRecording(false);

    // Smart frame selection: pick diverse frames
    const selectedFrames = selectBestFrames(frames, 10);
    setCapturedFrames(selectedFrames);

    toast.success(`${selectedFrames.length} frame terbaik terpilih!`);
  };

  const selectBestFrames = (frames, targetCount) => {
    if (frames.length <= targetCount) return frames;

    // Select frames evenly distributed
    const step = Math.floor(frames.length / targetCount);
    const selected = [];

    for (let i = 0; i < frames.length; i += step) {
      if (selected.length >= targetCount) break;
      selected.push(frames[i]);
    }

    return selected;
  };

  const resetCapture = () => {
    setCapturedFrames([]);
    setProgress(0);
    setCurrentInstruction("center");
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Camera Preview */}
      <div className="relative bg-gray-900 rounded-xl overflow-hidden">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          className="w-full h-auto"
        />

        {/* Countdown Overlay */}
        {countdown !== null && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-70">
            <div className="text-white text-9xl font-bold animate-pulse">
              {countdown}
            </div>
          </div>
        )}

        {/* Recording Instructions */}
        {isRecording && (
          <div className="absolute inset-0 pointer-events-none">
            {/* Face Guide Circle */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-80 h-96 border-4 border-green-500 rounded-full opacity-50"></div>
            </div>

            {/* Instruction Text */}
            <div className="absolute top-8 left-0 right-0 text-center">
              <div className="inline-block bg-green-500 text-white px-8 py-4 rounded-full text-xl font-bold shadow-lg animate-pulse">
                {
                  instructions.find((i) => i.position === currentInstruction)
                    ?.text
                }
              </div>
            </div>

            {/* Progress Bar */}
            <div className="absolute bottom-8 left-8 right-8">
              <div className="bg-gray-800 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-green-500 h-full transition-all duration-100 ease-linear"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-white text-center mt-2 text-sm">
                Mengambil data wajah... {Math.round(progress)}%
              </p>
            </div>
          </div>
        )}

        {/* Preview Captured Frames */}
        {capturedFrames.length > 0 && !isRecording && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-black bg-opacity-70 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white text-sm font-semibold">
                  ✅ {capturedFrames.length} frame siap
                </span>
                <button
                  onClick={resetCapture}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Ulangi
                </button>
              </div>
              <div className="flex gap-1 overflow-x-auto">
                {capturedFrames.slice(0, 5).map((frame, idx) => (
                  <img
                    key={idx}
                    src={frame}
                    alt={`Frame ${idx + 1}`}
                    className="w-16 h-16 object-cover rounded"
                  />
                ))}
                {capturedFrames.length > 5 && (
                  <div className="w-16 h-16 bg-gray-700 rounded flex items-center justify-center text-white text-xs">
                    +{capturedFrames.length - 5}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Instructions Panel */}
      {!isRecording && capturedFrames.length === 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
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
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Cara Scan Wajah:
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• Pastikan wajah Anda berada dalam pencahayaan yang baik</li>
            <li>• Posisikan wajah di tengah kamera</li>
            <li>• Ikuti instruksi gerakan kepala (kiri, kanan, atas, bawah)</li>
            <li>• Proses hanya memakan waktu ~5 detik</li>
            <li>• Sistem akan otomatis mengambil frame terbaik</li>
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        {capturedFrames.length === 0 ? (
          <button
            onClick={startRecording}
            disabled={isRecording || countdown !== null}
            className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg"
          >
            {countdown !== null
              ? `Mulai dalam ${countdown}...`
              : isRecording
              ? "Sedang Merekam..."
              : "🎥 Mulai Scan Wajah"}
          </button>
        ) : (
          <button
            onClick={() => onComplete(capturedFrames)}
            className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg"
          >
            ✓ Lanjutkan Registrasi ({capturedFrames.length} frame)
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoRegistration;
