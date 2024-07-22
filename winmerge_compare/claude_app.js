import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const CareerBuddy = () => {
  const [apiKey, setApiKey] = useState("");
  const [apiType, setApiType] = useState("openai");
  const [modelName, setModelName] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescriptionFile, setJobDescriptionFile] = useState(null);
  const [pitches, setPitches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [trialUsed, setTrialUsed] = useState(0);
  const [userId, setUserId] = useState("");

  useEffect(() => {
    const storedTrialUsed = localStorage.getItem("trialUsed");
    if (storedTrialUsed) {
      setTrialUsed(parseInt(storedTrialUsed, 10));
    }
    setUserId(Math.random().toString(36).substring(7));
  }, []);

  const handleFileUpload = (event, setFile) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setFile(file);
    } else {
      setError("Please upload a PDF file.");
    }
  };

  const handleGeneratePitch = async () => {
    if (!resumeFile || !jobDescriptionFile) {
      setError("Please upload both resume and job description PDFs.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      let data = new FormData();
      data.append("apiType", apiType);
      data.append("apiKey", apiKey);
      data.append("userId", userId);
      data.append("resumeFile", resumeFile);
      data.append("jobDescriptionFile", jobDescriptionFile);

      if (apiType === "hf") {
        data.append("modelName", modelName);
      }

      const response = await axios.post(`${API_URL}/generate-pitches`, data, {
        headers: {
          "Content-Type": "multipart/form-data",
          "User-ID": userId,
        },
      });

      setPitches(response.data.pitches);
      const newTrialUsed = trialUsed + 1;
      setTrialUsed(newTrialUsed);
      localStorage.setItem("trialUsed", newTrialUsed.toString());
    } catch (err) {
      console.error("Error generating pitches:", err);
      setError(`Failed to generate pitches: ${err.response?.data?.error || err.message}`);
    }
    setIsLoading(false);
  };

  return (
    <div>
      <h1>CareerBuddy: Your AI Career Fair Assistant</h1>
      
      {trialUsed < 3 ? (
        <div>
          <p>Trial uses remaining: {3 - trialUsed}</p>
          <input type="file" accept=".pdf" onChange={(e) => handleFileUpload(e, setResumeFile)} />
          <input type="file" accept=".pdf" onChange={(e) => handleFileUpload(e, setJobDescriptionFile)} />
          <button onClick={handleGeneratePitch} disabled={isLoading}>
            {isLoading ? "Generating..." : "Generate Pitches"}
          </button>
        </div>
      ) : (
        <div>
          <p>Trial period has ended. Please choose an API to continue:</p>
          <select value={apiType} onChange={(e) => setApiType(e.target.value)}>
            <option value="openai">OpenAI</option>
            <option value="hf">Hugging Face</option>
          </select>
          <input 
            type="text" 
            placeholder="Enter your API key" 
            value={apiKey} 
            onChange={(e) => setApiKey(e.target.value)} 
          />
          {apiType === "hf" && (
            <input 
              type="text" 
              placeholder="Enter model name" 
              value={modelName} 
              onChange={(e) => setModelName(e.target.value)} 
            />
          )}
          <input type="file" accept=".pdf" onChange={(e) => handleFileUpload(e, setResumeFile)} />
          <input type="file" accept=".pdf" onChange={(e) => handleFileUpload(e, setJobDescriptionFile)} />
          <button onClick={handleGeneratePitch} disabled={isLoading}>
            {isLoading ? "Generating..." : "Generate Pitches"}
          </button>
        </div>
      )}

      {error && <p style={{color: 'red'}}>{error}</p>}

      {pitches.length > 0 && (
        <div>
          <h2>Your Personalized Pitches</h2>
          {pitches.map((pitch, index) => (
            <div key={index}>
              <h3>Pitch {index + 1}</h3>
              <p>{pitch}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CareerBuddy;