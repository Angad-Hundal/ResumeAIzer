import { useState } from 'react';
import './job_description.css';

const JobDescriptionInput = ({ onDescriptionChange }) => {
  const [description, setDescription] = useState('');

  const handleChange = (e) => {
    const text = e.target.value;
    setDescription(text);
    onDescriptionChange(text);
  };

  return (
    <div className="job-description-input">
      <h3>Job Description</h3>
      <textarea
        value={description}
        onChange={handleChange}
        placeholder="Paste the job description here..."
        rows={8}
        className="description-textarea"
      />
      <p className="character-count">
        {description.length} characters
      </p>
    </div>
  );
};

export default JobDescriptionInput;