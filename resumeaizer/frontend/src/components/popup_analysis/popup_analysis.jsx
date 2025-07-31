import React, { useEffect } from 'react';
import './popup_analysis.css';

const PopupAnalysis = ({ response, onClose }) => {
  useEffect(() => {
    if (response?.success) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [response, onClose]);

  if (!response) return null;

  return (
    <div className={`popup-overlay ${response.success ? 'success' : 'error'}`}>
      <div className="popup-content">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>
        
        {response.success ? (
          <>
            <h3>Analysis Complete!</h3>
            <p>File: {response.filename}</p>
            
            {response.analysis && (
              <div className="analysis-summary">
                <h4>Summary:</h4>
                <ul>
                  {Object.entries(response.analysis).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key.replace(/_/g, ' ')}:</strong> {value.toString()}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {response.critique && (
              <div className="critique-section">
                <h4>Critique:</h4>
                <p>{response.critique}</p>
              </div>
            )}
            
            {response.market_trends && (
              <div className="market-trends">
                <h4>Market Trends:</h4>
                <p>{response.market_trends}</p>
              </div>
            )}
            
            <div className="metrics">
              <p>Iterations: {response.iterations}</p>
              <p>Satisfaction Score: {response.satisfaction_score}/10</p>
            </div>
          </>
        ) : (
          <>
            <h3>Error Processing Request</h3>
            <p className="error-message">{response.error}</p>
            <p className="error-type">Error type: {response.error_type}</p>
          </>
        )}
      </div>
    </div>
  );
};

export default PopupAnalysis;