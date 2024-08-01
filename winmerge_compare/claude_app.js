import React, { useState, useEffect } from "react";
import axios from "axios";
import AudioPlayer from "./components/AudioPlayer";
import PracticeModal from "./components/PracticeModal";
import AnalysisResults from "./components/AnalysisResults";

const API_URL = window.location.hostname === "localhost" 
  ? "http://localhost:5000" 
  : "https://careerbuddy-54b5c7a8058b.herokuapp.com";

const CareerBuddy = () => {
  // ... (keep existing state variables) ...
  const [audioData, setAudioData] = useState({});
  const [practiceMode, setPracticeMode] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [currentPitch, setCurrentPitch] = useState(null);

  // ... (keep existing functions) ...

  const handleGenerateAudio = async (pitchText, index) => {
    try {
      const response = await axios.post(`${API_URL}/generate-audio`, { pitchText });
      setAudioData(prevData => ({
        ...prevData,
        [index]: response.data.audioData
      }));
    } catch (error) {
      console.error("Error generating audio:", error);
      setError("Failed to generate audio. Please try again.");
    }
  };

  const handlePractice = (pitch, index) => {
    setCurrentPitch({ text: pitch, index });
    setPracticeMode(true);
  };

  const handlePracticeComplete = async (audioBlob, videoBlob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'practice_audio.wav');
      formData.append('video', videoBlob, 'practice_video.mp4');

      const response = await axios.post(`${API_URL}/analyze-practice`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setAnalysisResults(response.data);
      setPracticeMode(false);
    } catch (error) {
      console.error("Error analyzing practice:", error);
      setError("Failed to analyze practice. Please try again.");
      setPracticeMode(false);
    }
  };

  // ... (keep existing JSX) ...

  {pitches.map((pitch, index) => (
    <div key={index} className="bg-gray-100 p-6 rounded-lg mb-6 shadow-md">
      <h4 className="text-lg font-semibold mb-2 text-blue-600">Pitch {index + 1}</h4>
      <p className="text-gray-800 leading-relaxed whitespace-pre-line">{pitch}</p>
      <div className="mt-4 space-x-2">
        <button
          onClick={() => handleGenerateAudio(pitch, index)}
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
        >
          Generate Audio
        </button>
        {audioData[index] && (
          <AudioPlayer audioData={audioData[index]} />
        )}
        <button
          onClick={() => handlePractice(pitch, index)}
          className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition-colors"
        >
          Practice
        </button>
      </div>
    </div>
  ))}

  {practiceMode && (
    <PracticeModal
      pitch={currentPitch.text}
      onComplete={handlePracticeComplete}
      onCancel={() => setPracticeMode(false)}
    />
  )}

  {analysisResults && (
    <AnalysisResults
      results={analysisResults}
      onClose={() => setAnalysisResults(null)}
    />
  )}

  // ... (keep existing JSX) ...

};

export default CareerBuddy;