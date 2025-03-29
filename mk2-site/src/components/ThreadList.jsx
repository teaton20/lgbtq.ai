import React from 'react';

function ThreadList() {
  const threads = [
    { id: 1, name: "Thread 1" },
    { id: 2, name: "Thread 2" },
  ];

  return (
    <ul className="thread-list">
      {threads.map(thread => (
        <li key={thread.id}>{thread.name}</li>
      ))}
    </ul>
  );
}

export default ThreadList;
