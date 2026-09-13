import React from 'react';
import { GitBranch, Star, Clock, Activity, Settings } from 'lucide-react';
import './RepositoryCard.css';

interface RepositoryCardProps {
  name: string;
  description: string;
  stars: number;
  branches: number;
  lastSync: string;
  status: 'healthy' | 'warning' | 'error' | 'analyzing';
  score: number;
  onClick: () => void;
  onSettingsClick?: (e: React.MouseEvent) => void;
}

export function RepositoryCard({
  name,
  description,
  stars,
  branches,
  lastSync,
  status,
  score,
  onClick,
  onSettingsClick
}: RepositoryCardProps) {
  const statusColor = {
    healthy: 'var(--color-success)',
    warning: 'var(--color-warning)',
    error: 'var(--color-danger)',
    analyzing: 'var(--color-info)'
  }[status];

  return (
    <div className="card card-interactive repo-card" onClick={onClick}>
      <div className="repo-card-header">
        <div className="repo-title-group">
          <div className="repo-icon">
            <svg viewBox="0 0 16 16" width="20" height="20" fill="currentColor">
              <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"></path>
            </svg>
          </div>
          <div>
            <h3 className="repo-name">{name}</h3>
            <span className="repo-status" style={{ color: statusColor }}>
              <span className="status-dot" style={{ backgroundColor: statusColor }} />
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </div>
        </div>
        {onSettingsClick && (
          <button className="btn btn-ghost btn-icon" onClick={onSettingsClick} aria-label="Settings">
            <Settings size={18} />
          </button>
        )}
      </div>

      <p className="repo-description">{description || 'No description provided.'}</p>

      <div className="repo-metrics">
        <div className="metric">
          <Star size={16} />
          <span>{stars}</span>
        </div>
        <div className="metric">
          <GitBranch size={16} />
          <span>{branches}</span>
        </div>
        <div className="metric">
          <Activity size={16} />
          <span className={`score score-${score >= 80 ? 'good' : score >= 60 ? 'warn' : 'bad'}`}>
            {score} IQ
          </span>
        </div>
      </div>

      <div className="repo-footer">
        <div className="repo-sync">
          <Clock size={14} />
          <span>Updated {lastSync}</span>
        </div>
      </div>
    </div>
  );
}
