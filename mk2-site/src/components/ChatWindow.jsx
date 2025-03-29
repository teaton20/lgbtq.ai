import React from 'react';

function ChatWindow() {
  return (
    <div className="chat-window">
      <div className="message user-message">User: Hello!</div>
      <div className="message ai-message">AI: Hi, how can I help you?</div>
    </div>
  );
}

export default ChatWindow;
