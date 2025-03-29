import React, { useState } from 'react';
import HeroSearch from '../components/HeroSearch';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import MainLayout from '../layouts/MainLayout';

function Home() {
  const [searchSubmitted, setSearchSubmitted] = useState(false);

  const handleSearchSubmit = (query) => {
    // Process the search query, e.g., start a chat session.
    console.log("Search submitted:", query);
    setSearchSubmitted(true);
  };

  return (
    <MainLayout>
      {!searchSubmitted ? (
        <HeroSearch onSubmit={handleSearchSubmit} />
      ) : (
        <>
          <ChatWindow />
          <ChatInput />
        </>
      )}
    </MainLayout>
  );
}

export default Home;
