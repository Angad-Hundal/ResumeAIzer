import React from 'react';
import './model_selector.css';

const ModelSelector = ({ selectedModel, onModelChange }) => {
  const models = [
    { id: 'huggingface', name: 'Hugging Face AI Agent' },
    { id: 'github', name: 'GitHub AI Agent' }
  ];

  return (
    <div className="model-selector">
      <label htmlFor="ai-model">Select AI Model:</label>
      <select
        id="ai-model"
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value)}
        className="model-dropdown"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;