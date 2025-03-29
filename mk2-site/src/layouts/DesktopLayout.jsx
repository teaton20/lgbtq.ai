import React from 'react';
import Sidebar from '../components/Sidebar';

function DesktopLayout({ children }) {
  return (
    <div className="desktop-layout">
      <Sidebar />
      <div className="main-content">
        {children}
      </div>
    </div>
  );
}

export default DesktopLayout;
