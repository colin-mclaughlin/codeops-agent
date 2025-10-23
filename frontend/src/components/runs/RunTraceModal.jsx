import { useState } from 'react';

export default function RunTraceModal({ isOpen, onClose, trace, loading }) {
  const [expandedSteps, setExpandedSteps] = useState({});

  if (!isOpen) return null;

  const toggleStepExpansion = (index) => {
    setExpandedSteps(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-2xl shadow-xl border border-gray-700 max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">
            Run Trace - #{trace?.run_id || 'Loading...'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-400">Loading trace data...</div>
            </div>
          ) : trace ? (
            <div className="space-y-6">
              {/* GitHub Operations Summary */}
              {trace.result && (trace.result.github_branch || trace.result.github_commit || trace.result.test_runner) && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Operations Summary</h3>
                  <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Branch Information */}
                      {(trace.result.github_branch || trace.result.github_commit) && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">GitHub Operations</h4>
                          <div className="space-y-2">
                            {trace.result.github_branch && (
                              <div>
                                <span className="text-xs text-gray-400">Branch:</span>
                                <div className="font-mono text-sm text-blue-400">
                                  {trace.result.github_branch.branch}
                                </div>
                              </div>
                            )}
                            {trace.result.github_commit && (
                              <div>
                                <span className="text-xs text-gray-400">Commit SHA:</span>
                                <div className="font-mono text-sm text-green-400">
                                  {trace.result.github_commit.commit_sha}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Test Results */}
                      {trace.result.test_runner && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Test Results</h4>
                          <div className="space-y-2">
                            <div>
                              <span className="text-xs text-gray-400">Status:</span>
                              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                                trace.result.test_runner.status === 'success' 
                                  ? 'text-green-400 bg-green-400/10'
                                  : trace.result.test_runner.status === 'fail'
                                  ? 'text-red-400 bg-red-400/10'
                                  : 'text-yellow-400 bg-yellow-400/10'
                              }`}>
                                {trace.result.test_runner.status}
                              </span>
                            </div>
                            {trace.result.test_runner.command && (
                              <div>
                                <span className="text-xs text-gray-400">Command:</span>
                                <div className="font-mono text-sm text-gray-300">
                                  {trace.result.test_runner.command}
                                </div>
                              </div>
                            )}
                            {trace.result.test_runner.output && (
                              <div>
                                <span className="text-xs text-gray-400">Output:</span>
                                <div className="bg-gray-800 rounded p-2 font-mono text-xs text-gray-200 max-h-32 overflow-y-auto">
                                  {trace.result.test_runner.output}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Agent Steps */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Agent Steps</h3>
                <div className="space-y-4">
                  {trace.agent_steps?.map((step, index) => (
                    <div key={index} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="bg-blue-600 text-white px-2 py-1 rounded text-sm font-medium">
                            {step.tool}
                          </span>
                          <span className="text-gray-300 text-sm">
                            {formatTimestamp(step.ts)}
                          </span>
                        </div>
                        <button
                          onClick={() => toggleStepExpansion(index)}
                          className="text-blue-400 hover:text-blue-300 text-sm"
                        >
                          {expandedSteps[index] ? 'Show Less' : 'Show More'}
                        </button>
                      </div>
                      
                      <div className="space-y-3">
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-1">Input:</h4>
                          <div className="bg-gray-800 rounded p-3 font-mono text-sm text-gray-200">
                            {expandedSteps[index] ? step.input : truncateText(step.input)}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-1">Output:</h4>
                          <div className="bg-gray-800 rounded p-3 font-mono text-sm text-gray-200">
                            {expandedSteps[index] ? step.output : truncateText(step.output)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Critic Section */}
              {trace.critic && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Critic Analysis</h3>
                  <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">Summary:</h4>
                        <p className="text-gray-200">{trace.critic.summary}</p>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-1">Confidence:</h4>
                          <div className="flex items-center gap-2">
                            <div className="bg-gray-800 rounded px-3 py-1">
                              <span className="text-yellow-400 font-semibold">
                                {(trace.critic.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-24 bg-gray-600 rounded-full h-2">
                              <div 
                                className="bg-yellow-400 h-2 rounded-full" 
                                style={{ width: `${trace.critic.confidence * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {trace.critic.notes && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Notes:</h4>
                          <p className="text-gray-200">{trace.critic.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-400">No trace data available</div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
