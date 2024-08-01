import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = window.location.hostname === "localhost" 
  ? "http://localhost:5000" 
  : "https://careerbuddy-54b5c7a8058b.herokuapp.com";

const AnalysisResults = ({ results, onClose, isTrialMode, apiType, apiKey, userId, modelName }) => {
  const [feedback, setFeedback] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchFeedback = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/generate-feedback`, {
        analysisResults: results,
        isTrialMode: isTrialMode,
        apiType: apiType,
        apiKey: apiKey,
        userId: userId,
        modelName: modelName
      });
      if (response.data && response.data.feedback) {
        setFeedback(response.data.feedback);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching feedback:', error);
      setError(error.response?.data?.error || error.message || 'Failed to generate AI feedback. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [results, isTrialMode, apiType, apiKey, userId, modelName]);

  useEffect(() => {
    fetchFeedback();
  }, [fetchFeedback]);

  const renderEmotionList = (emotions, title) => (
    <div className="mb-6">
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <ul className="list-disc pl-5">
        {emotions.map(([emotion, score], index) => (
          <li key={index} className="mb-1">
            {emotion}: {(score * 100).toFixed(2)}%
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-4xl w-full">
        <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>
        
        {renderEmotionList(results.audioAnalysis.topEmotions, "Audio Analysis (Top 5 Characteristics)")}
        {renderEmotionList(results.videoAnalysis.topEmotions, "Video Analysis (Top 5 Characteristics)")}

        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">AI-Generated Feedback</h3>
          {isLoading ? (
            <p>Generating feedback... This may take a moment.</p>
          ) : error ? (
            <div>
              <p className="text-red-500">{error}</p>
              <button
                onClick={fetchFeedback}
                className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : (
            <div className="whitespace-pre-wrap">{feedback}</div>
          )}
        </div>

        <button
          onClick={onClose}
          className="mt-6 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default AnalysisResults;