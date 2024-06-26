import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

function App() {
  const [resume, setResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [pitches, setPitches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/generate-pitches`, { resume, jobDescription });
      setPitches(response.data.pitches);
    } catch (err) {
      setError('Failed to generate pitches. Please try again.');
      console.error(err);
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 className="text-2xl font-bold mb-5">CareerBuddy: AI Pitch Generator</h1>
          <form onSubmit={handleSubmit} className="mb-5">
            <div className="mb-4">
              <label htmlFor="resume" className="block text-sm font-medium text-gray-700">Resume</label>
              <textarea
                id="resume"
                value={resume}
                onChange={(e) => setResume(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                rows="4"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700">Job Description</label>
              <textarea
                id="jobDescription"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                rows="4"
                required
              />
            </div>
            <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" disabled={isLoading}>
              {isLoading ? 'Generating...' : 'Generate Pitches'}
            </button>
          </form>
          {error && <p className="text-red-500">{error}</p>}
          {pitches.map((pitch, index) => (
            <div key={index} className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h2 className="text-lg font-semibold mb-2">Pitch {index + 1}</h2>
              <p>{pitch}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;