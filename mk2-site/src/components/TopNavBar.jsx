import React from 'react';
import { Link } from 'react-router-dom';
import QuickExitButton from './QuickExitButton';

function TopNavBar() {
  return (
    <nav className="top-nav">
      <div className="nav-left">
        <Link to="/" className="logo">The Product</Link>
      </div>
      <div className="nav-center">
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/support">Support</Link>
      </div>
      <div className="nav-right">
        <QuickExitButton />
      </div>
    </nav>
  );
}

export default TopNavBar;
