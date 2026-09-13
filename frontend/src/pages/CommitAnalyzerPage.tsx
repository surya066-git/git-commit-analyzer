import React, { useState } from 'react';
import { useToast } from '../context/ToastContext';
import { GitCommit, FileCode, CheckCircle, XCircle, AlertTriangle, Play, RefreshCw, Copy } from 'lucide-react';
import './CommitAnalyzerPage.css';

interface AnalysisResult {
    category: string;
    confidence: number;
    qualityScore: number;
    qualityLevel: string;
    qualityBreakdown: {
        clarity: number;
        specificity: number;
        actionability: number;
        context: number;
        consistency: number;
    };
    issues: string[];
    suggestion: string;
    consistency: {
        status: string;
        reason: string;
    };
}

export default function CommitAnalyzerPage() {
    const { showToast } = useToast();
    const [message, setMessage] = useState('');
    const [changedFiles, setChangedFiles] = useState('');
    const [additions, setAdditions] = useState<number | ''>('');
    const [deletions, setDeletions] = useState<number | ''>('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);

    const handleAnalyze = async () => {
        if (!message.trim()) {
            showToast('Commit message is required', 'error');
            return;
        }

        setLoading(true);
        setResult(null);

        try {
            const filesArray = changedFiles.split('\n').map(f => f.trim()).filter(f => f);
            
            const request = {
                commitMessage: message,
                changedFiles: filesArray,
                additions: additions === '' ? 0 : Number(additions),
                deletions: deletions === '' ? 0 : Number(deletions)
            };

            const response = await fetch('http://localhost:3000/api/commits/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => null);
                throw new Error(errData?.error || 'Failed to analyze commit');
            }

            const data = await response.json();
            setResult(data);
            showToast('Commit analyzed successfully.', 'success');
        } catch (err: any) {
            showToast(err.message || 'Unable to analyze commit.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        if (result?.suggestion) {
            navigator.clipboard.writeText(result.suggestion);
            showToast('Suggestion copied to clipboard.', 'success');
        }
    };

    return (
        <div className="page-container analyzer-page">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Commit Analyzer</h1>
                    <p className="page-subtitle">Analyze individual commit messages using our ML pipeline</p>
                </div>
            </header>

            <div className="analyzer-layout">
                {/* LEFT PANEL */}
                <div className="analyzer-input-panel card">
                    <h2 className="panel-title">Commit Details</h2>
                    
                    <div className="form-group">
                        <label>Commit Message</label>
                        <textarea 
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="e.g. fix stuff"
                            rows={4}
                            className="input-control"
                        />
                    </div>

                    <div className="form-group">
                        <label>Changed Files (one per line)</label>
                        <textarea 
                            value={changedFiles}
                            onChange={(e) => setChangedFiles(e.target.value)}
                            placeholder="src/auth/login.ts&#10;src/auth/token.ts"
                            rows={4}
                            className="input-control"
                        />
                    </div>

                    <div className="stats-row">
                        <div className="form-group">
                            <label>Additions (+)</label>
                            <input 
                                type="number" 
                                value={additions}
                                onChange={(e) => setAdditions(e.target.value ? Number(e.target.value) : '')}
                                placeholder="0"
                                className="input-control text-success"
                            />
                        </div>
                        <div className="form-group">
                            <label>Deletions (-)</label>
                            <input 
                                type="number" 
                                value={deletions}
                                onChange={(e) => setDeletions(e.target.value ? Number(e.target.value) : '')}
                                placeholder="0"
                                className="input-control text-danger"
                            />
                        </div>
                    </div>

                    <button 
                        className="btn btn-primary btn-block mt-4" 
                        onClick={handleAnalyze}
                        disabled={loading}
                    >
                        {loading ? (
                            <><RefreshCw className="spin" size={18} /> Processing NLP...</>
                        ) : (
                            <><Play size={18} /> Analyze Commit</>
                        )}
                    </button>
                </div>

                {/* RIGHT PANEL */}
                <div className="analyzer-result-panel">
                    {!result && !loading && (
                        <div className="empty-state card h-full flex-center text-center">
                            <GitCommit size={48} className="text-tertiary mb-4" />
                            <h3>Ready to Analyze</h3>
                            <p className="text-secondary mt-2">Enter your commit details on the left and click Analyze Commit to see real-time AI insights.</p>
                        </div>
                    )}

                    {loading && (
                        <div className="loading-state card h-full flex-center text-center">
                            <div className="loader-spinner mb-4" />
                            <h3>Running Pipeline</h3>
                            <p className="text-secondary mt-2">Preparing text &rarr; Running classifier &rarr; Evaluating quality...</p>
                        </div>
                    )}

                    {result && !loading && (
                        <div className="result-dashboard">
                            {/* Score Card */}
                            <div className="card score-card flex items-center justify-between">
                                <div>
                                    <h3 className="text-sm font-medium text-secondary uppercase tracking-wider">Quality Score</h3>
                                    <div className="flex items-end gap-2 mt-2">
                                        <span className={`text-4xl font-bold color-${result.qualityLevel.toLowerCase()}`}>
                                            {result.qualityScore}
                                        </span>
                                        <span className="text-xl text-tertiary font-medium mb-1">/ 100</span>
                                    </div>
                                    <div className={`badge badge-${result.qualityLevel.toLowerCase()} mt-2`}>
                                        {result.qualityLevel}
                                    </div>
                                </div>
                                <div className="score-circle">
                                    <svg viewBox="0 0 36 36" className={`circular-chart ${result.qualityLevel.toLowerCase()}`}>
                                        <path className="circle-bg"
                                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                        />
                                        <path className="circle"
                                            strokeDasharray={`${result.qualityScore}, 100`}
                                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                        />
                                    </svg>
                                </div>
                            </div>

                            {/* Classification */}
                            <div className="card">
                                <h3 className="panel-title">Classification</h3>
                                <div className="flex justify-between items-center mt-4">
                                    <div className="flex items-center gap-3">
                                        <div className="category-icon">
                                            <FileCode size={20} />
                                        </div>
                                        <div>
                                            <div className="text-lg font-semibold">{result.category}</div>
                                            <div className="text-sm text-secondary">
                                                Confidence: {(result.confidence * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Issues */}
                            {result.issues.length > 0 && (
                                <div className="card">
                                    <h3 className="panel-title text-danger flex items-center gap-2">
                                        <AlertTriangle size={18} /> Quality Issues
                                    </h3>
                                    <ul className="issues-list mt-3">
                                        {result.issues.map((issue, idx) => (
                                            <li key={idx} className="issue-item">
                                                <div className="issue-bullet"></div>
                                                {issue}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Consistency */}
                            <div className={`card consistency-card status-${result.consistency.status.toLowerCase()}`}>
                                <h3 className="panel-title flex items-center gap-2">
                                    {result.consistency.status === 'CONSISTENT' ? (
                                        <><CheckCircle size={18} className="text-success"/> Consistent</>
                                    ) : (
                                        <><AlertTriangle size={18} className="text-warning"/> Potential Mismatch</>
                                    )}
                                </h3>
                                <p className="mt-2 text-sm">{result.consistency.reason}</p>
                            </div>

                            {/* Recommendation Card */}
                            <div className="card suggestion-card">
                                <h3 className="panel-title uppercase tracking-wider text-xs font-bold text-accent">Recommended Commit Message</h3>
                                
                                <div className="suggestion-box mt-4">
                                    <div className="text-sm text-secondary mb-1">Original:</div>
                                    <div className="original-text">{message}</div>
                                    
                                    <div className="text-sm text-secondary mb-1 mt-4">Suggested:</div>
                                    <div className="suggested-text">{result.suggestion}</div>
                                </div>

                                <div className="flex gap-3 mt-4">
                                    <button className="btn btn-primary flex-1" onClick={handleCopy}>
                                        <Copy size={16} /> Copy Suggestion
                                    </button>
                                    <button className="btn btn-outline flex-1" onClick={handleAnalyze}>
                                        <RefreshCw size={16} /> Analyze Again
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
