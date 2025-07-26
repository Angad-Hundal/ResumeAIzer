import React, { useState } from 'react';
import './home.css';
import ResumeUploader from '../resume_uploader/resume_uploader';
import JobDescriptionInput from '../job_description/job_description';
import Analysis from '../analysis/analysis';

const downloadBase64Pdf = (base64Data, filename) => {
  const linkSource = `data:application/pdf;base64,${base64Data}`;
  const downloadLink = document.createElement('a');
  downloadLink.href = linkSource;
  downloadLink.download = filename;
  downloadLink.click();
};

const Home = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

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

    try {
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process resume');
      }

      const result = await response.json();
      console.log('Backend response:', result);
    
      if (result.updated_resume) {
        downloadBase64Pdf(result.updated_resume, result.filename || 'updated_resume.pdf');} 
        else {
        alert('Resume was processed but no updated PDF returned.');}
      
      if (result.analysis) {
        setAnalysisData(result.analysis);
      } else {
        setAnalysisData(null);
      }

    } catch (error) {
      console.error('Error:', error);
      alert('Error processing resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home">
      <h1>Resume Customizer</h1>
      <div className="upload-container">
        <ResumeUploader onFileSelect={setResumeFile} />
        <JobDescriptionInput onDescriptionChange={setJobDescription} />
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={!resumeFile || !jobDescription.trim() || loading}
        >
          {loading ? 'Processing...' : 'Process Resume'}
        </button>
      </div>

      {analysisData && <Analysis data={analysisData} />}
    </div>
  );
};

export default Home;