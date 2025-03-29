import React from 'react';
import DiscoverCard from './DiscoverCard';
import DiscoverFilters from './DiscoverFilters';

function DiscoverFeed() {
  const cards = [
    { title: "News 1", snippet: "Snippet for news 1", time: "2 hrs ago", source: "Source A" },
    { title: "News 2", snippet: "Snippet for news 2", time: "4 hrs ago", source: "Source B" },
    // More dummy cards can be added here.
  ];

  return (
    <div className="discover-feed">
      <DiscoverFilters />
      <div className="card-feed">
        {cards.map((card, index) => (
          <DiscoverCard key={index} {...card} />
        ))}
      </div>
    </div>
  );
}

export default DiscoverFeed;
