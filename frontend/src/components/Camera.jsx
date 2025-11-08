import React, { useRef, useState, useCallback } from "react";
import Webcam from "react-webcam";

const Camera = ({ onCapture, countdown = 3, autoCapture = false }) => {
  const webcamRef = useRef(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [countdownValue, setCountdownValue] = useState(null);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: "user",
    frameRate: { ideal: 30, max: 60 },
  };

  const handleUserMedia = () => {
    setIsCameraReady(true);
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot({
      width: 1280,
      height: 720,
    });
    if (imageSrc && onCapture) {
      onCapture(imageSrc);
    }
  }, [webcamRef, onCapture]);

  const captureWithCountdown = () => {
    let count = countdown;
    setCountdownValue(count);

    const interval = setInterval(() => {
      count -= 1;
      setCountdownValue(count);

      if (count === 0) {
        clearInterval(interval);
        capture();
        setTimeout(() => setCountdownValue(null), 500);
      }
    }, 1000);
  };

  return (
    <div className="relative w-full">
      <div className="relative bg-gray-900 rounded-lg overflow-hidden">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          onUserMedia={handleUserMedia}
          className="w-full h-auto"
        />

        {/* Countdown overlay */}
        {countdownValue !== null && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="text-white text-9xl font-bold animate-pulse">
              {countdownValue}
            </div>
          </div>
        )}

        {/* Camera not ready overlay */}
        {!isCameraReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white">Memuat kamera...</p>
            </div>
          </div>
        )}
      </div>

      {/* Capture button */}
      {isCameraReady && !autoCapture && (
        <button
          onClick={captureWithCountdown}
          disabled={countdownValue !== null}
          className="mt-4 w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {countdownValue !== null ? "Mengambil gambar..." : "Ambil Foto"}
        </button>
      )}
    </div>
  );
};

export default Camera;
