import React from 'react';

function QuickExitButton() {
  const handleQuickExit = () => {
    // Redirect to a safe page (e.g., Google)
    window.location.href = 'https://www.google.com';
  };

  return (
    <button className="quick-exit" onClick={handleQuickExit}>
      Quick Exit
    </button>
  );
}

export default QuickExitButton;
