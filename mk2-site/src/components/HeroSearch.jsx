import React, { useState } from 'react';

function HeroSearch({ onSubmit }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(query);
  };

  return (
    <div className="hero-search">
      <h1>Let’s get started</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="What would you like to do?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>
    </div>
  );
}

export default HeroSearch;
