import React, { useState } from 'react';
import './home.css';
import ResumeUploader from '../resume_uploader/resume_uploader';
import JobDescriptionInput from '../job_description/job_description';
import Analysis from '../analysis/analysis';
import ModelSelector from '../model_selector/model_selector';
import PopupAnalysis from '../popup_analysis/popup_analysis';

const Home = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('github'); 
  const [apiResponse, setApiResponse] = useState(null);
  const [showPopup, setShowPopup] = useState(false);

  const handleSubmit = async () => {
    if (!resumeFile || !jobDescription.trim()) {
      alert('Please upload a resume and enter job description');
      return;
    }

    setLoading(true);
    setAnalysisData(null);

    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);
    formData.append('model', selectedModel);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/process`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      console.log('Backend response:', result);

      if (!response.ok) {
        setApiResponse({
          success: false,
          error: result.error || 'Failed to process resume',
          error_type: result.error_type || 'api_error'
        });
        setShowPopup(true);
        return;
      }

      setApiResponse(result);
      setShowPopup(true);
      
      if (result.analysis) {
        setAnalysisData(result.analysis);
      } else {
        setAnalysisData(null);
      }

    } catch (error) {
      console.error('Error:', error);
      setApiResponse({
        success: false,
        error: error.message || 'Error processing resume',
        error_type: 'network_error'
      });
      setShowPopup(true);
    } finally {
      setLoading(false);
    }
  };

  const closePopup = () => {
    setShowPopup(false);
    setApiResponse(null);
  };


  return (
    <div className="home">
      <h1>Resume Analyzer</h1>
      <div className="upload-container">
        <ResumeUploader onFileSelect={setResumeFile} />
        <JobDescriptionInput onDescriptionChange={setJobDescription} />
        <ModelSelector 
          selectedModel={selectedModel} 
          onModelChange={setSelectedModel} 
        />
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={!resumeFile || !jobDescription.trim() || loading}
        >
          {loading ? 'Processing...' : 'Process Resume'}
        </button>
      </div>

      {analysisData && <Analysis data={analysisData} />}

      {showPopup && apiResponse && (
        <PopupAnalysis response={apiResponse} onClose={closePopup} />
      )}
    </div>
  );
};

export default Home;