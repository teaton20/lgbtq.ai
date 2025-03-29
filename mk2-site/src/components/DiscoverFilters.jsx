import React, { useState } from 'react';

function DiscoverFilters() {
  const [topic, setTopic] = useState('');
  const [source, setSource] = useState('');

  const handleFilterChange = (e) => {
    // Handle filter changes (e.g., update state or dispatch to global state)
    console.log("Filter changed", e.target.name, e.target.value);
    if(e.target.name === 'topic') setTopic(e.target.value);
    if(e.target.name === 'source') setSource(e.target.value);
  };

  return (
    <div className="discover-filters">
      <select name="topic" value={topic} onChange={handleFilterChange}>
        <option value="">Select Topic</option>
        <option value="technology">Technology</option>
        <option value="lgbtq">LGBTQ</option>
      </select>
      <select name="source" value={source} onChange={handleFilterChange}>
        <option value="">Select Source</option>
        <option value="sourceA">Source A</option>
        <option value="sourceB">Source B</option>
      </select>
    </div>
  );
}

export default DiscoverFilters;
