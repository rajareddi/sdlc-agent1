import React, { useState } from "react";

const SDLC_PHASES = [
  "Planning",
  "Analysis",
  "Design",
  "Implementation",
  "Testing",
  "Maintenance"
];

const API_BASE_URL = "http://127.0.0.1:8000";

function WizardStep({ phase, draft, checklist, onApprove, approved, onEdit, loading }) {
  return (
    <div className="border rounded p-4 mb-6 bg-white shadow">
      <h2 className="text-xl font-bold mb-2">Phase: {phase}</h2>
      <label className="block mb-2 font-semibold">Draft Output</label>
      {loading ? (
        <div className="w-full border p-4 mb-2 bg-gray-100 rounded flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">AI is generating draft...</span>
        </div>
      ) : (
        <textarea
          className="w-full border p-2 mb-2"
          value={draft}
          onChange={e => onEdit(e.target.value)}
          disabled={approved}
          rows={12}
          placeholder="AI-generated draft will appear here..."
        />
      )}
      <div className="mb-2">
        <label className="font-semibold">Checklist for Human Review:</label>
        <ul className="list-disc ml-6">
          {checklist.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      </div>
      <button
        className={`px-4 py-2 rounded bg-blue-600 text-white font-bold ${approved ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-700"}`}
        onClick={onApprove}
        disabled={approved || loading}
      >
        {approved ? "✓ Approved" : "Approve"}
      </button>
    </div>
  );
}

export default function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [drafts, setDrafts] = useState(Array(SDLC_PHASES.length).fill(""));
  const [checklists, setChecklists] = useState(Array(SDLC_PHASES.length).fill([]));
  const [approved, setApproved] = useState(Array(SDLC_PHASES.length).fill(false));
  const [loading, setLoading] = useState(false);
  const [projectContext, setProjectContext] = useState("Build a modern e-commerce web application with user authentication, product catalog, shopping cart, and payment processing.");
  const [error, setError] = useState("");

  const handleApprove = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/approve-draft`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phase: SDLC_PHASES[currentStep],
          approved_content: drafts[currentStep]
        })
      });

      if (response.ok) {
        const newApproved = [...approved];
        newApproved[currentStep] = true;
        setApproved(newApproved);
        setError("");
      } else {
        setError("Failed to approve draft");
      }
    } catch (err) {
      setError("Network error: " + err.message);
    }
  };

  const handleEdit = (value) => {
    const newDrafts = [...drafts];
    newDrafts[currentStep] = value;
    setDrafts(newDrafts);
  };

  const handleRunStep = async () => {
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch(`${API_BASE_URL}/generate-draft`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phase: SDLC_PHASES[currentStep],
          project_context: projectContext
        })
      });

      if (response.ok) {
        const data = await response.json();
        const newDrafts = [...drafts];
        const newChecklists = [...checklists];
        
        newDrafts[currentStep] = data.draft_output;
        newChecklists[currentStep] = data.checklist;
        
        setDrafts(newDrafts);
        setChecklists(newChecklists);
      } else {
        const errorData = await response.json();
        setError(`Failed to generate draft: ${errorData.detail}`);
      }
    } catch (err) {
      setError("Network error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (approved[currentStep] && currentStep < SDLC_PHASES.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">🌀 SDLC Agent Wizard</h1>
      <p className="text-center text-gray-600 mb-6">AI-powered SDLC with LangGraph Orchestrator + Human-in-the-Loop</p>
      
      {/* Project Context Input */}
      <div className="mb-6 p-4 bg-gray-50 rounded">
        <label className="block mb-2 font-semibold">Project Context:</label>
        <textarea
          className="w-full border p-2 rounded"
          value={projectContext}
          onChange={e => setProjectContext(e.target.value)}
          rows={3}
          placeholder="Describe your project..."
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {/* Progress Bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-300"
            style={{ width: `${((currentStep + 1) / SDLC_PHASES.length) * 100}%` }}
          ></div>
        </div>
        <div className="text-center mt-2 font-semibold">
          Step {currentStep + 1} of {SDLC_PHASES.length}: {SDLC_PHASES[currentStep]}
        </div>
      </div>
      
      {/* Run Step Button */}
      <button
        className={`mb-4 px-6 py-3 rounded font-bold ${
          drafts[currentStep] || loading 
            ? "bg-gray-400 cursor-not-allowed" 
            : "bg-green-600 hover:bg-green-700 text-white"
        }`}
        onClick={handleRunStep}
        disabled={!!drafts[currentStep] || loading}
      >
        {loading ? "Generating..." : "🚀 Generate AI Draft"}
      </button>
      
      {/* Wizard Step */}
      <WizardStep
        phase={SDLC_PHASES[currentStep]}
        draft={drafts[currentStep]}
        checklist={checklists[currentStep]}
        onApprove={handleApprove}
        approved={approved[currentStep]}
        onEdit={handleEdit}
        loading={loading}
      />
      
      {/* Navigation Buttons */}
      <div className="flex gap-4">
        <button
          className={`px-4 py-2 rounded font-bold ${
            currentStep === 0 
              ? "bg-gray-300 cursor-not-allowed" 
              : "bg-gray-600 hover:bg-gray-700 text-white"
          }`}
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
        >
          ← Previous
        </button>
        
        <button
          className={`px-4 py-2 rounded font-bold ${
            approved[currentStep] && currentStep < SDLC_PHASES.length - 1
              ? "bg-purple-600 hover:bg-purple-700 text-white" 
              : "bg-gray-300 cursor-not-allowed"
          }`}
          onClick={handleNext}
          disabled={!approved[currentStep] || currentStep === SDLC_PHASES.length - 1}
        >
          Next →
        </button>
      </div>
      
      {/* Completion Message */}
      {currentStep === SDLC_PHASES.length - 1 && approved[currentStep] && (
        <div className="mt-6 p-4 bg-green-100 border border-green-400 rounded text-center font-bold text-green-700">
          🎉 All steps approved! SDLC Document is complete.
        </div>
      )}
    </div>
  );
}
