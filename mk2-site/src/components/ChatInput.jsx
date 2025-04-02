import React, { useState } from 'react';
import { sendChatMessage } from '../utils/api';
import FollowUpSuggestions from './FollowUpSuggestions';

function ChatInput() {
  const [input, setInput] = useState('');
  const [followUpMode, setFollowUpMode] = useState(false);
  const [chatResponse, setChatResponse] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting message:", input);
    const result = await sendChatMessage(input);
    if (result.response) {
      setChatResponse(result.response);
    } else {
      setChatResponse("Error: " + result.error);
    }
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
      {chatResponse && (
        <div className="chat-response">
          <strong>Bot:</strong> {chatResponse}
        </div>
      )}
    </div>
  );
}

export default ChatInput;