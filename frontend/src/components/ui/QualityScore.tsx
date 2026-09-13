import React, { useEffect, useState } from 'react';
import type { QualityLevel, QualityBreakdown } from '../../types';

const QUALITY_CONFIG: Record<QualityLevel, { color: string; label: string; bg: string }> = {
  excellent: { color: '#22c55e', label: 'Excellent', bg: 'rgba(34,197,94,0.1)' },
  good:      { color: '#3b82f6', label: 'Good',      bg: 'rgba(59,130,246,0.1)' },
  moderate:  { color: '#f59e0b', label: 'Moderate',  bg: 'rgba(245,158,11,0.1)' },
  poor:      { color: '#ef4444', label: 'Poor',      bg: 'rgba(239,68,68,0.1)' },
};

export function getQualityLevel(score: number): QualityLevel {
  if (score >= 90) return 'excellent';
  if (score >= 75) return 'good';
  if (score >= 50) return 'moderate';
  return 'poor';
}

interface QualityScoreCircleProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
}

export function QualityScoreCircle({ score, size = 80, strokeWidth = 6, showLabel = true }: QualityScoreCircleProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const level = getQualityLevel(score);
  const cfg = QUALITY_CONFIG[level];
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (animatedScore / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => {
      const start = Date.now();
      const duration = 800;
      const animate = () => {
        const elapsed = Date.now() - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        setAnimatedScore(Math.round(eased * score));
        if (progress < 1) requestAnimationFrame(animate);
      };
      requestAnimationFrame(animate);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="quality-score-circle" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="var(--bg-elevated)" strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={cfg.color} strokeWidth={strokeWidth}
          strokeDasharray={`${progress} ${circumference}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.8s cubic-bezier(0.4,0,0.2,1)', filter: `drop-shadow(0 0 6px ${cfg.color}66)` }}
        />
      </svg>
      <div className="quality-score-value" style={{ color: cfg.color }}>
        <div style={{ fontSize: size * 0.22, fontWeight: 700, lineHeight: 1, textAlign: 'center' }}>
          {animatedScore}
        </div>
        {showLabel && (
          <div style={{ fontSize: size * 0.12, color: 'var(--text-tertiary)', textAlign: 'center', marginTop: 2 }}>
            /100
          </div>
        )}
      </div>
    </div>
  );
}

interface QualityBadgeProps {
  level: QualityLevel;
  size?: 'sm' | 'md';
}

export function QualityBadge({ level, size = 'md' }: QualityBadgeProps) {
  const cfg = QUALITY_CONFIG[level];
  return (
    <span className="badge" style={{
      background: cfg.bg,
      color: cfg.color,
      border: `1px solid ${cfg.color}33`,
      fontSize: size === 'sm' ? '10px' : '11px',
    }}>
      {cfg.label}
    </span>
  );
}

interface QualityBreakdownBarProps {
  breakdown: QualityBreakdown;
}

export function QualityBreakdownBars({ breakdown }: QualityBreakdownBarProps) {
  const dimensions = [
    { key: 'clarity' as const,       label: 'Clarity',       max: 20 },
    { key: 'specificity' as const,   label: 'Specificity',   max: 20 },
    { key: 'actionability' as const, label: 'Actionability', max: 20 },
    { key: 'context' as const,       label: 'Context',       max: 20 },
    { key: 'consistency' as const,   label: 'Consistency',   max: 20 },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      {dimensions.map(dim => {
        const val = breakdown[dim.key];
        const pct = (val / dim.max) * 100;
        const level = getQualityLevel((val / dim.max) * 100);
        const color = QUALITY_CONFIG[level].color;
        return (
          <div key={dim.key}>
            <div className="flex items-center justify-between mb-1">
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', fontWeight: 500 }}>{dim.label}</span>
              <span style={{ fontSize: 'var(--text-xs)', color, fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                {val}/{dim.max}
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${pct}%`, background: color, boxShadow: `0 0 6px ${color}44` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
