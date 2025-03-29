import React from 'react';

function DiscoverCard({ title, snippet, time, source }) {
  return (
    <div className="discover-card">
      <h3>{title}</h3>
      <p>{snippet}</p>
      <div className="card-meta">
        <span>{time}</span>
        <span>{source}</span>
      </div>
    </div>
  );
}

export default DiscoverCard;
