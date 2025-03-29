import React from 'react';

function FollowUpSuggestions() {
  const suggestions = [
    "Tell me more",
    "More details",
    "Related topics",
  ];

  return (
    <div className="follow-up-suggestions">
      {suggestions.map((suggestion, index) => (
        <span key={index} className="suggestion-chip">
          {suggestion}
        </span>
      ))}
    </div>
  );
}

export default FollowUpSuggestions;
