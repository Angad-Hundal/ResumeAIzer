import React, { useState } from 'react';
import axios from 'axios';

const PdfUploader = () => {
  const [uploadState, setUploadState] = useState({
    isUploading: false,
    message: '',
    results: null,
    error: null
  });

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type === 'application/pdf') {
      setUploadState({
        ...uploadState,
        error: 'Please select a PDF file'
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadState({
        isUploading: true,
        message: 'Uploading and processing PDF...',
        results: null,
        error: null
      });

      const response = await axios.post('http://localhost:8000/pdf/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUploadState({
        isUploading: false,
        message: 'PDF processed successfully!',
        results: response.data.results,
        error: null
      });

    } catch (error) {
      const errorMsg = error.response?.data?.detail || 
                     error.message || 
                     'Failed to process PDF';
      
      setUploadState({
        isUploading: false,
        message: '',
        results: null,
        error: errorMsg
      });
    }
  };

  return (
    <div className="pdf-uploader">
      <h2>PDF Upload and Parser</h2>
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        disabled={uploadState.isUploading}
      />
      
      {uploadState.isUploading && <p>Processing PDF...</p>}
      {uploadState.message && <p className="success">{uploadState.message}</p>}
      {uploadState.error && <p className="error">{uploadState.error}</p>}
      
      {uploadState.results && (
        <div className="results">
          <h3>PDF Analysis Results:</h3>
          <ul>
            <li>File size: {Math.round(uploadState.results.file_size / 1024)} KB</li>
            <li>Pages: {uploadState.results.page_count}</li>
            {uploadState.results.emails && (
              <li>Emails found: {uploadState.results.emails.join(', ')}</li>
            )}
          </ul>
          <h4>Extracted Text Preview:</h4>
          <pre>{uploadState.results.text.substring(0, 500)}...</pre>
        </div>
      )}
    </div>
  );
};

export default PdfUploader;