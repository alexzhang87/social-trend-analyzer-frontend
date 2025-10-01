import React, { useState } from 'react';

const WorkspacePage: React.FC = () => {
  const [showQuickStart, setShowQuickStart] = useState(true);
  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  const features = [
    {
      id: 'trend-analysis',
      label: 'Trend Analysis',
      description: 'Analyze social media trends and keyword performance'
    },
    {
      id: 'audience-insights',
      label: 'Audience Insights',
      description: 'Understand your audience demographics and behavior'
    },
    {
      id: 'data-analytics',
      label: 'Data Analytics',
      description: 'Advanced analytics and reporting tools'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Quick Start Modal */}
      {showQuickStart && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Quick Start Analysis</h2>
              <button 
                onClick={() => setShowQuickStart(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <p className="text-gray-600 mb-4">Welcome to the workspace! Let's start your first analysis.</p>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">1. Choose Analysis Type</h3>
                <p className="text-sm text-gray-600">Select the analysis feature you want from the left menu</p>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">2. Enter Keywords</h3>
                <p className="text-sm text-gray-600">Enter the keywords or topics you want to analyze</p>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">3. View Results</h3>
                <p className="text-sm text-gray-600">Get detailed analysis reports and insights</p>
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <button 
                onClick={() => setShowQuickStart(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              >
                Skip
              </button>
              <button 
                onClick={() => setShowQuickStart(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 p-4">
          <h1 className="text-lg font-semibold mb-6">Workspace</h1>
          <p className="text-sm text-gray-600 mb-4">Select analysis features</p>
          
          <div className="space-y-2">
            {features.map((feature) => (
              <button
                key={feature.id}
                onClick={() => setActiveFeature(feature.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                  activeFeature === feature.id 
                    ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="w-5 h-5 bg-blue-600 rounded"></div>
                <span className="font-medium">{feature.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          {activeFeature ? (
            <div className="p-6">
              {(() => {
                const feature = features.find(f => f.id === activeFeature);
                if (!feature) return null;
                
                return (
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-6 h-6 bg-blue-600 rounded"></div>
                      <h2 className="text-2xl font-semibold">{feature.label}</h2>
                    </div>
                    <p className="text-gray-600 mb-6">{feature.description}</p>
                    
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                      <h3 className="font-medium mb-4">Getting Started</h3>
                      <p className="text-gray-600 mb-4">
                        This feature is currently in development. More functionality will be available soon.
                      </p>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        Learn More
                      </button>
                    </div>
                  </div>
                );              })()}
            </div>
          ) : (
            <div className="p-6">
              <div className="text-center py-12">
                <h2 className="text-xl font-semibold mb-2">Select a feature to start analysis</h2>
                <p className="text-gray-600 mb-4">Welcome, free user</p>
                
                <div className="max-w-2xl mx-auto">
                  <h3 className="font-medium mb-4">Workspace</h3>
                  <button 
                    onClick={() => setShowQuickStart(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mr-2"
                  >
                    Quick Start
                  </button>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                    {features.map((feature) => (
                      <button
                        key={feature.id}
                        onClick={() => setActiveFeature(feature.id)}
                        className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
                      >
                        <div className="w-8 h-8 bg-blue-600 rounded mb-3"></div>
                        <h4 className="font-medium mb-2">{feature.label}</h4>
                        <p className="text-sm text-gray-600">{feature.description}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default WorkspacePage;