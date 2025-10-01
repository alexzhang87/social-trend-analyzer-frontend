import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WorkspacePage from './pages/WorkspacePage';
import TestPage from './pages/TestPage';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Routes>
          <Route path="/test" element={<TestPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/" element={<div className="p-8"><h1 className="text-2xl font-bold">Welcome to the App</h1><p className="mt-4"><a href="/workspace" className="text-blue-600 hover:underline">Go to Workspace</a></p></div>} />
          <Route path="*" element={<div className="p-8"><h1 className="text-2xl font-bold">Page Not Found</h1><p className="mt-4"><a href="/" className="text-blue-600 hover:underline">Go Home</a></p></div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;