import React from 'react';
import './popup_analysis.css';

const PopupAnalysis = ({ response, onClose }) => {

  console.log('PopupAnalysis response:', response);
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
            <p><strong>File:</strong> {response.filename}</p>

            {response.analysis && (
              <div className="analysis-summary">
                <h4>Summary:</h4>
                <div className="text-block">{response.analysis}</div>
              </div>
            )}

            {response.critique && (
              <div className="critique-section">
                <h4>Critique:</h4>
                <div className="text-block">{response.critique}</div>
              </div>
            )}

            {response.market_trends && (
              <div className="market-trends">
                <h4>Market Trends:</h4>
                <div className="text-block">{response.market_trends}</div>
              </div>
            )}

            <div className="metrics">
              <p><strong>Iterations:</strong> {response.iterations}</p>
              <p><strong>Satisfaction Score:</strong> {response.satisfaction_score}/10</p>
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
