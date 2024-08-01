import React, { useState, useRef, useEffect, useCallback } from 'react';

const PracticeModal = ({ pitch, onComplete, onCancel }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [countdown, setCountdown] = useState(3);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const videoChunks = useRef([]);
  const timerRef = useRef(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
          videoChunks.current.push(event.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const videoBlob = new Blob(videoChunks.current, { type: 'video/mp4' });
        onComplete(audioBlob, videoBlob, "Transcription placeholder");  // Add actual transcription logic here
      };

      mediaRecorder.current.start();
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  }, [onComplete]);

  useEffect(() => {
    let timer;
    if (isRecording && countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else if (isRecording && countdown === 0) {
      startRecording();
    }
    return () => clearTimeout(timer);
  }, [isRecording, countdown, startRecording]);

  useEffect(() => {
    if (isRecording && countdown === 0) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prevTime) => prevTime + 0.1);
      }, 100);
    }
    return () => clearInterval(timerRef.current);
  }, [isRecording, countdown]);

  const handleStartRecording = () => {
    setIsRecording(true);
    setCountdown(3);
    setRecordingTime(0);
  };

  const handleStopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      console.log('MediaRecorder stopped');
      
      // Wait for the 'onstop' event to fire
      mediaRecorder.current.onstop = () => {
        console.log('onstop event fired');
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const videoBlob = new Blob(videoChunks.current, { type: 'video/mp4' });
        
        console.log('Audio Blob size:', audioBlob.size);
        console.log('Video Blob size:', videoBlob.size);
        
        onComplete(audioBlob, videoBlob, "Transcription placeholder");
      };
    }
    setIsRecording(false);
    clearInterval(timerRef.current);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-2xl w-full">
        <h2 className="text-2xl font-bold mb-4">Practice Your Pitch</h2>
        <p className="mb-4">{pitch}</p>
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
          >
            Start Recording
          </button>
        ) : countdown > 0 ? (
          <div className="text-4xl font-bold text-center">{countdown}</div>
        ) : (
          <div>
            <div className="flex items-center mb-4">
              <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse mr-2"></div>
              <span>Recording: {recordingTime.toFixed(1)}s</span>
            </div>
            <button
              onClick={handleStopRecording}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
            >
              Stop Recording
            </button>
          </div>
        )}
        <button
          onClick={onCancel}
          className="ml-4 bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default PracticeModal;