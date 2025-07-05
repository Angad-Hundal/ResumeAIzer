import { useState } from 'react';
import './resume_uploader.css';

const ResumeUploader = ({ onFileSelect }) => {
  const [fileName, setFileName] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setFileName(file.name);
        onFileSelect(file);
      } else {
        alert('Please select a PDF file');
      }
    }
  };

  return (
    <div className="resume-uploader">
      <h3>Upload Your Resume (PDF)</h3>
      <label className="file-input-label">
        {fileName || 'Choose file...'}
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="file-input"
        />
      </label>
      {fileName && <p className="file-info">Selected: {fileName}</p>}
    </div>
  );
};

export default ResumeUploader;