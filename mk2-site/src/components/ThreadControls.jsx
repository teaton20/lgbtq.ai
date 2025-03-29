import React from 'react';

function ThreadControls({ threadId }) {
  const handleRename = () => {
    console.log("Rename thread", threadId);
  };

  const handleDelete = () => {
    console.log("Delete thread", threadId);
  };

  return (
    <div className="thread-controls">
      <button onClick={handleRename}>Rename</button>
      <button onClick={handleDelete}>Delete</button>
    </div>
  );
}

export default ThreadControls;
