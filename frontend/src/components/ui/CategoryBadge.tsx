import React from 'react';
import type { CommitCategory } from '../../types';

const CATEGORY_CONFIG: Record<CommitCategory, { label: string; color: string; bg: string; dot: string }> = {
  FEATURE:       { label: 'Feature',       color: '#818cf8', bg: 'rgba(99,102,241,0.12)',  dot: '#6366f1' },
  BUG_FIX:       { label: 'Bug Fix',       color: '#f87171', bg: 'rgba(239,68,68,0.12)',   dot: '#ef4444' },
  REFACTORING:   { label: 'Refactoring',   color: '#fbbf24', bg: 'rgba(245,158,11,0.12)',  dot: '#f59e0b' },
  TESTING:       { label: 'Testing',       color: '#4ade80', bg: 'rgba(34,197,94,0.12)',   dot: '#22c55e' },
  DOCUMENTATION: { label: 'Docs',          color: '#60a5fa', bg: 'rgba(59,130,246,0.12)',  dot: '#3b82f6' },
  CONFIGURATION: { label: 'Config',        color: '#c084fc', bg: 'rgba(139,92,246,0.12)',  dot: '#8b5cf6' },
  PERFORMANCE:   { label: 'Performance',   color: '#fb923c', bg: 'rgba(249,115,22,0.12)',  dot: '#f97316' },
  SECURITY:      { label: 'Security',      color: '#f472b6', bg: 'rgba(236,72,153,0.12)',  dot: '#ec4899' },
  OTHER:         { label: 'Other',         color: '#94a3b8', bg: 'rgba(148,163,184,0.12)', dot: '#64748b' },
};

interface CategoryBadgeProps {
  category: CommitCategory;
  size?: 'sm' | 'md';
  showDot?: boolean;
}

export function CategoryBadge({ category, size = 'md', showDot = true }: CategoryBadgeProps) {
  const cfg = CATEGORY_CONFIG[category];
  return (
    <span
      className="badge"
      style={{
        background: cfg.bg,
        color: cfg.color,
        fontSize: size === 'sm' ? '10px' : '11px',
        padding: size === 'sm' ? '2px 6px' : '3px 8px',
        border: `1px solid ${cfg.color}22`,
      }}
    >
      {showDot && (
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: cfg.dot, flexShrink: 0,
          display: 'inline-block',
        }} />
      )}
      {cfg.label}
    </span>
  );
}

export { CATEGORY_CONFIG };
