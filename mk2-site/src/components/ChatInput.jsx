import React, { useState } from 'react';
import FollowUpSuggestions from './FollowUpSuggestions';

function ChatInput() {
  const [input, setInput] = useState('');
  const [followUpMode, setFollowUpMode] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Submitted:", input);
    setInput('');
  };

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
      {followUpMode && <FollowUpSuggestions />}
      <button onClick={() => setFollowUpMode(!followUpMode)}>
        {followUpMode ? 'Hide Suggestions' : 'Show Suggestions'}
      </button>
    </div>
  );
}

export default ChatInput;
