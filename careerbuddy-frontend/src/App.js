import React, { useState } from 'react';
import axios from 'axios';

const MockStreamlit = ({ children }) => (
  <div className="bg-gray-100 min-h-screen p-8">
    <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md">
      {children}
    </div>
  </div>
);

const Button = ({ children, onClick, disabled }) => (
  <button
    className={`bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

const TextArea = ({ label, placeholder, value, onChange }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
    <textarea
      className="w-full p-2 border border-gray-300 rounded"
      rows="4"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
    ></textarea>
  </div>
);

const Icon = ({ d }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="inline mr-2">
    <path d={d} />
  </svg>
);

const FileUploadIcon = () => (
  <Icon d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
);

const UploadIcon = () => (
  <Icon d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
);

const CareerBuddy = () => {
  const [resume, setResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [pitches, setPitches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGeneratePitch = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/generate-pitches', {
        resume,
        jobDescription
      });
      setPitches(response.data.pitches);
    } catch (err) {
      setError('Failed to generate pitches. Please try again.');
      console.error(err);
    }
    setIsLoading(false);
  };

  return (
    <MockStreamlit>
      <h1 className="text-3xl font-bold mb-6">CareerBuddy: Your AI Career Fair Assistant</h1>
      
      <h2 className="text-2xl font-semibold mb-4">Upload Your Resume</h2>
      <div className="mb-4">
        <Button>
          <FileUploadIcon />
          Choose a PDF file
        </Button>
      </div>
      
      <TextArea
        label="Or paste your resume text here:"
        placeholder="Enter your resume text..."
        value={resume}
        onChange={(e) => setResume(e.target.value)}
      />
      
      <h2 className="text-2xl font-semibold mb-4">Enter Job Description</h2>
      <TextArea
        label="Paste the job description here:"
        placeholder="Enter the job description..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />
      
      <Button onClick={handleGeneratePitch} disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Generate Pitches'}
      </Button>
      
      {error && <p className="text-red-500 mt-4">{error}</p>}
      
      {pitches.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">Your Personalized Pitches</h3>
          {pitches.map((pitch, index) => (
            <div key={index} className="bg-gray-100 p-4 rounded mb-4">
              <h4 className="font-semibold">Pitch {index + 1}</h4>
              <p>{pitch}</p>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-8 bg-gray-200 p-4 rounded">
        <h2 className="text-xl font-semibold mb-4">About CareerBuddy</h2>
        <p className="mb-4">
          CareerBuddy is an AI-powered webapp that helps you create personalized
          pitches for career fairs. Simply upload your resume and paste the job
          description to get an instant pitch that aligns your skills and experience
          with the job requirements.
        </p>
        
        <h2 className="text-xl font-semibold mb-4">Future Feature</h2>
        <p>
          <UploadIcon />
          Image upload for resumes coming soon!
        </p>
      </div>
    </MockStreamlit>
  );
}

export default CareerBuddy;