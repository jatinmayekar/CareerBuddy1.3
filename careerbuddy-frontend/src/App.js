import React, { useState } from 'react';
import axios from 'axios';

//const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const API_URL = 'https://careerbuddy-54b5c7a8058b.herokuapp.com' || 'http://localhost:5000';

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

const Input = ({ label, type, placeholder, value, onChange }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
    <input
      type={type}
      className="w-full p-2 border border-gray-300 rounded focus:border-blue-500 focus:ring focus:ring-blue-200"
      placeholder={placeholder}
      value={value}
      onChange={onChange}
    />
  </div>
);

const MicrophoneIcon = () => (
  <Icon d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z M19 10v2a7 7 0 0 1-14 0v-2 M12 19v4 M8 23h8" />
);

const PlayIcon = () => (
  <Icon d="M5 3l14 9-14 9V3z" />
);

const CopyButton = ({ text }) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
    >
      {isCopied ? 'Copied!' : 'Copy to Clipboard'}
    </button>
  );
};

const InvestorForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    interest: '',
    reason: '',
    amount: '',
  });
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post(`${API_URL}/submit-investor-form`, formData);
      console.log('Form submitted:', response.data);
      setIsSubmitted(true);
    } catch (error) {
      console.error('Error submitting form:', error);
      setError('Failed to submit form. Please try again later.');
    }
  };

  if (isSubmitted) {
    return (
      <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4" role="alert">
        <p className="font-bold">Thank you for your interest in CareerBuddy!</p>
        <p>We'll be in touch soon with more information.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label htmlFor="interest" className="block text-sm font-medium text-gray-700">I'm interested in:</label>
        <select
          id="interest"
          name="interest"
          value={formData.interest}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        >
          <option value="">Select an option</option>
          <option value="investing">Investing in CareerBuddy</option>
          <option value="waitlist">Joining the Waitlist</option>
          <option value="both">Both Investing and Joining the Waitlist</option>
        </select>
      </div>
      <div>
        <label htmlFor="reason" className="block text-sm font-medium text-gray-700">
          {formData.interest === 'investing' ? 'Why do you want to invest?' : 
           formData.interest === 'waitlist' ? 'What features are you most excited about?' :
           'Tell us more about your interest in CareerBuddy'}
        </label>
        <textarea
          id="reason"
          name="reason"
          value={formData.reason}
          onChange={handleChange}
          required
          rows="4"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        ></textarea>
      </div>
      {(formData.interest === 'investing' || formData.interest === 'both') && (
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700">Potential investment amount</label>
          <input
            type="text"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            placeholder="e.g., $10,000"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          />
        </div>
      )}
      <button
        type="submit"
        className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Submit
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </form>
  );
};

const CareerBuddy = () => {
  const [apiKey, setApiKey] = useState('');
  const [apiType, setApiType] = useState('hf');
  const [resume, setResume] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [pitches, setPitches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  const [trialUsed, setTrialUsed] = useState(0);

  useEffect(() => {
    // Load trial usage from localStorage
    const storedTrialUsed = localStorage.getItem('trialUsed');
    if (storedTrialUsed) {
      setTrialUsed(parseInt(storedTrialUsed, 10));
    }
  }, []);

  const validateApiKey = async () => {
    try {
      const response = await axios.post(`${API_URL}/validate-api-key`, { apiKey });
      return response.data.isValid;
    } catch (err) {
      console.error('Error validating API key:', err);
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error data:', err.response.data);
        console.error('Error status:', err.response.status);
        console.error('Error headers:', err.response.headers);
      } else if (err.request) {
        // The request was made but no response was received
        console.error('Error request:', err.request);
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error message:', err.message);
      }
      setError(`Error validating API key: ${err.message}`);
      return false;
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
    } else {
      setError('Please upload a PDF file.');
    }
  };

  // const handleGeneratePitch = async () => {
  //   if (!apiKey) {
  //     setError('Please enter your OpenAI API key.');
  //     return;
  //   }

  //   if (!resumeFile && !resume) {
  //     setError('Please provide a resume (either text or PDF file).');
  //     return;
  //   }

  //   if (!jobDescription) {
  //     setError('Please enter a job description.');
  //     return;
  //   }

  //   setIsLoading(true);
  //   setError('');
  //   setDebugInfo('');

  //   const isValidKey = await validateApiKey();
  //   if (!isValidKey) {
  //     setIsLoading(false);
  //     return;
  //   }

  //   try {
  //     let data;
  //     let headers = {};
      
  //     if (resumeFile) {
  //       data = new FormData();
  //       data.append('apiKey', apiKey);
  //       data.append('jobDescription', jobDescription);
  //       data.append('resumeFile', resumeFile);
  //       headers['Content-Type'] = 'multipart/form-data';
  //     } else if (resume) {
  //       data = { apiKey, jobDescription, resume };
  //       headers['Content-Type'] = 'application/json';
  //     } else {
  //       throw new Error('Please provide a resume (either text or PDF file).');
  //     }

  //     const response = await axios.post(`${API_URL}/generate-pitches`, data, { headers });
  //     setPitches(response.data.pitches);
  //     setDebugInfo(JSON.stringify(response.data, null, 2));
  //   } catch (err) {
  //     console.error('Error generating pitches:', err);
  //     setError(`Failed to generate pitches: ${err.response?.data?.error || err.message}`);
  //     setDebugInfo(JSON.stringify(err.response?.data, null, 2));
  //   }
  //   setIsLoading(false);
  // };

  const handleGeneratePitch = async () => {
    if (trialUsed >= 3 && apiType === 'hf') {
      setError('Trial expired. Please use OpenAI API or switch to the free Hugging Face option.');
      return;
    }

    if (apiType === 'openai' && !apiKey) {
      setError('Please enter your OpenAI API key.');
      return;
    }

    if (!resumeFile && !resume) {
      setError('Please provide a resume (either text or PDF file).');
      return;
    }

    if (!jobDescription) {
      setError('Please enter a job description.');
      return;
    }

    setIsLoading(true);
    setError('');
    setDebugInfo('');

    try {
      let data = new FormData();
      data.append('apiType', apiType);
      data.append('jobDescription', jobDescription);
      
      if (resumeFile) {
        data.append('resumeFile', resumeFile);
      } else {
        data.append('resume', resume);
      }

      if (apiType === 'openai') {
        data.append('apiKey', apiKey);
      }

      const response = await axios.post(`${API_URL}/generate-pitches`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      setPitches(response.data.pitches);
      if (apiType === 'hf') {
        const newTrialUsed = trialUsed + 1;
        setTrialUsed(newTrialUsed);
        localStorage.setItem('trialUsed', newTrialUsed.toString());
      }
      setDebugInfo(JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Error generating pitches:', err);
      setError(`Failed to generate pitches: ${err.response?.data?.error || err.message}`);
      setDebugInfo(JSON.stringify(err.response?.data, null, 2));
    }
    setIsLoading(false);
  };

  return (
    <MockStreamlit>
      <h1 className="text-3xl font-bold mb-6">CareerBuddy: Your AI Career Fair Assistant</h1>
      
      {trialUsed < 3 ? (
        <div className="mb-4 bg-blue-100 p-2 rounded">
          Hugging Face API Trial uses remaining: {3 - trialUsed}
        </div>
      ) : (
        <div className="mb-6 bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded-md">
          <h2 className="text-xl font-semibold mb-2 text-yellow-800">Trial Expired</h2>
          <p>Please choose an API to continue using CareerBuddy:</p>
          <select
            value={apiType}
            onChange={(e) => setApiType(e.target.value)}
            className="mt-2 p-2 border rounded"
          >
            <option value="hf">Hugging Face (Free, but less accurate)</option>
            <option value="openai">OpenAI (Requires API Key, more accurate)</option>
          </select>
        </div>
      )}
      
      {apiType === 'openai' && (
        <div className="mb-6 bg-blue-100 border-l-4 border-blue-500 p-4 rounded-md">
          <h2 className="text-xl font-semibold mb-2 text-blue-800">API Configuration</h2>
          <Input
            label="Enter your OpenAI API Key:"
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <p className="text-sm text-blue-600 mt-2">
            Your API key is required to use GPT-4o for generating pitches. It's stored securely and never shared.
          </p>
        </div>
      )}
      
      <h2 className="text-2xl font-semibold mb-4">Upload Your Resume</h2>
      <div className="mb-4">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          className="hidden"
          id="resume-upload"
        />
        <label htmlFor="resume-upload" className="cursor-pointer bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
          <FileUploadIcon />
          Choose a PDF file
        </label>
        {resumeFile && <p className="mt-2">Selected file: {resumeFile.name}</p>}
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
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating...
          </>
        ) : 'Generate Pitches'}
      </Button>
      
      {error && <p className="text-red-500 mt-4">{error}</p>}
      
      {pitches.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-4">Your Personalized Pitches</h3>
          {pitches.map((pitch, index) => (
            <div key={index} className="bg-gray-100 p-6 rounded-lg mb-6 shadow-md">
              <h4 className="text-lg font-semibold mb-2 text-blue-600">Pitch {index + 1}</h4>
              <p className="text-gray-800 leading-relaxed whitespace-pre-line">{pitch}</p>
              <CopyButton text={pitch} />
            </div>
          ))}
        </div>
      )}

      {debugInfo && (
        <div className="mt-6">
          <button
            onClick={() => setShowDebugInfo(!showDebugInfo)}
            className="text-blue-600 hover:text-blue-800 mb-2"
          >
            {showDebugInfo ? 'Hide' : 'Show'} Debug Information
          </button>
          {showDebugInfo && (
            <pre className="bg-gray-200 p-4 rounded overflow-x-auto text-sm">
              {debugInfo}
            </pre>
          )}
        </div>
      )}
      
      <div className="mt-8 bg-gray-200 p-4 rounded">
        <h2 className="text-xl font-semibold mb-4">About CareerBuddy</h2>
        <p className="mb-4">
          CareerBuddy is an AI-powered webapp created by Jatin Mayekar that helps you create personalized
          pitches for career fairs. Simply upload your resume and paste the job
          description to get an instant pitch that aligns your skills and experience
          with the job requirements.
        </p>

        <p> Jatin Mayekar Twitter: <a href="https://twitter.com/jatin_mayekar" style={{ color: '#0078ff' }}>@jatin_mayekar</a> </p>
        <p> Jatin Mayekar LinkedIn: <a href="https://www.linkedin.com/in/jatin-mayekar/" style={{ color: '#0078ff' }}>Jatin Mayekar</a> </p>
        
        <h2 className="text-xl font-semibold mb-4">Future Features</h2>
        <ul className="list-disc list-inside">
          <li className="mb-2">
            <UploadIcon />
            Investor Form
          </li>
          <li className="mb-2">
            <UploadIcon />
            Waitlist subscription
          </li>
          <li className="mb-2">
            <PlayIcon />
            Listen to your generated pitch
          </li>
          <li>
            <MicrophoneIcon />
            Get feedback on your pitch based on Hume AI
          </li>
        </ul>
      </div>

      <div className="mt-8 bg-blue-100 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Join Our Journey: Invest or Get Early Access</h2>
        <p className="mb-4">
          CareerBuddy is growing, and we're excited to offer two ways for you to be part of our success:
        </p>
        <ul className="list-disc list-inside mb-4">
          <li className="mb-2">
            <strong>Invest in CareerBuddy:</strong> If you see the potential in our AI-powered career assistance platform and want to contribute to our growth, we'd love to discuss investment opportunities.
          </li>
          <li className="mb-2">
            <strong>Join our Waitlist:</strong> Be among the first to experience new features and updates. Get early access to upcoming capabilities like AI-powered interview feedback and personalized career coaching.
          </li>
        </ul>
        <p className="mb-4">
          Whether you're interested in investing or want to be at the forefront of AI-driven career development, fill out the form below. We'll reach out with more information tailored to your interests.
        </p>
        <InvestorForm />
      </div>
    </MockStreamlit>
  );
}

export default CareerBuddy;