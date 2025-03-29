import React from 'react';

function MainLayout({ children }) {
  return (
    <div className="main-layout">
      <div className="content-area">
        {children}
      </div>
    </div>
  );
}

export default MainLayout;
