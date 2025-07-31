import React, { useState } from 'react';
import './popup_analysis.css';

const PopupAnalysis = ({ response, onClose }) => {
  const [expandedSections, setExpandedSections] = useState({
    analysis: false,
    critique: false,
    marketTrends: false
  });

  const toggleSection = (section) => {
    setExpandedSections((prevState) => ({
      ...prevState,
      [section]: !prevState[section],
    }));
  };

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
              <div className="expandable-section">
                <button className="expand-toggle" onClick={() => toggleSection('analysis')}>
                  {expandedSections.analysis ? 'Collapse' : 'Expand'} Summary
                </button>
                {expandedSections.analysis && (
                  <div className="text-block">{response.analysis}</div>
                )}
              </div>
            )}

            {response.critique && (
              <div className="expandable-section">
                <button className="expand-toggle" onClick={() => toggleSection('critique')}>
                  {expandedSections.critique ? 'Collapse' : 'Expand'} Critique
                </button>
                {expandedSections.critique && (
                  <div className="text-block">{response.critique}</div>
                )}
              </div>
            )}

            {response.market_trends && (
              <div className="expandable-section">
                <button className="expand-toggle" onClick={() => toggleSection('marketTrends')}>
                  {expandedSections.marketTrends ? 'Collapse' : 'Expand'} Market Trends
                </button>
                {expandedSections.marketTrends && (
                  <div className="text-block">{response.market_trends}</div>
                )}
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
