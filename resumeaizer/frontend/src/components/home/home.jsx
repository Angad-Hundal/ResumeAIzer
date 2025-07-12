import React, { useState } from 'react';
import './home.css';
import ResumeUploader from '../resume_uploader/resume_uploader';
import JobDescriptionInput from '../job_description/job_description';

const Home = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  const handleSubmit = async () => {
    if (!resumeFile || !jobDescription.trim()) {
      alert('Please upload a resume and enter job description');
      return;
    }

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
      // Handle successful response (will implement PDF download in next iteration)

    } catch (error) {
      console.error('Error:', error);
      alert('Error processing resume. Please try again.');
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
          disabled={!resumeFile || !jobDescription.trim()}
        >
          Process Resume
        </button>
      </div>
    </div>
  );
};

export default Home;