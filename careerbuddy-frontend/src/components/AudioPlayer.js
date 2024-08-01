import React, { useState, useEffect } from 'react';

const AudioPlayer = ({ audioData }) => {
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (audioData) {
      try {
        // Assuming audioData is already a valid base64 string
        const audioBlob = new Blob([new Uint8Array(atob(audioData).split('').map(char => char.charCodeAt(0)))], { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setError(null);
      } catch (err) {
        console.error('Error creating audio URL:', err);
        setError('Failed to load audio. Please try again.');
      }
    }
  }, [audioData]);

  return (
    <div className="mt-2">
      {error ? (
        <p className="text-red-500">{error}</p>
      ) : audioUrl ? (
        <audio controls className="w-full">
          <source src={audioUrl} type="audio/wav" />
          Your browser does not support the audio element.
        </audio>
      ) : (
        <p>Loading audio...</p>
      )}
    </div>
  );
};

export default AudioPlayer;