import React from 'react';
import './analysis.css';

const Analysis = ({ data }) => {
  if (!data) {
    return null; // Render nothing if there's no data
  }

  const {
    keyword_match = [],
    missing_keywords = [],
    score,
    suggestions = [],
  } = data;

  return (
    <div className="analysis">
      <h2>Resume Analysis</h2>

      {typeof score === 'number' && (
        <div className="score-section">
          <strong>Match Score:</strong> <span className="score">{score}%</span>
        </div>
      )}

      {keyword_match.length > 0 && (
        <div className="section">
          <h3>Matched Keywords</h3>
          <ul>
            {keyword_match.map((word, index) => (
              <li key={index} className="matched">{word}</li>
            ))}
          </ul>
        </div>
      )}

      {missing_keywords.length > 0 && (
        <div className="section">
          <h3>Missing Keywords</h3>
          <ul>
            {missing_keywords.map((word, index) => (
              <li key={index} className="missing">{word}</li>
            ))}
          </ul>
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="section">
          <h3>Suggestions</h3>
          <ul>
            {suggestions.map((suggestion, index) => (
              <li key={index} className="suggestion">{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Analysis;
