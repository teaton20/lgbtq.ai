import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Discover from './pages/Discover';
import Support from './pages/Support';
import TopNavBar from './components/TopNavBar';

function App() {
  return (
    <Router>
      <div>
        <TopNavBar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/support" element={<Support />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
