import React from 'react';

function InlineCitation({ citation }) {
  return (
    <span className="inline-citation" title={`Citation: ${citation}`}>
      [i]
    </span>
  );
}

export default InlineCitation;
