import React from 'react';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  style?: React.CSSProperties;
}

export function Skeleton({ width = '100%', height = 16, borderRadius = 'var(--radius-md)', style }: SkeletonProps) {
  return (
    <div
      className="skeleton"
      style={{ width, height, borderRadius, ...style }}
    />
  );
}

export function SkeletonMetricCard() {
  return (
    <div className="metric-card">
      <Skeleton width={40} height={40} borderRadius="var(--radius-lg)" style={{ marginBottom: 'var(--space-4)' }} />
      <Skeleton width="60%" height={32} style={{ marginBottom: 'var(--space-2)' }} />
      <Skeleton width="80%" height={12} />
    </div>
  );
}

export function SkeletonCommitRow() {
  return (
    <tr>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}>
        <div className="flex items-center gap-3">
          <Skeleton width={28} height={28} borderRadius="50%" />
          <div style={{ flex: 1 }}>
            <Skeleton width="70%" height={14} style={{ marginBottom: 6 }} />
            <Skeleton width="40%" height={11} />
          </div>
        </div>
      </td>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}><Skeleton width="80px" height={14} /></td>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}><Skeleton width="60px" height={14} /></td>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}><Skeleton width="70px" height={22} borderRadius="var(--radius-full)" /></td>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}><Skeleton width="40px" height={14} /></td>
      <td style={{ padding: 'var(--space-3) var(--space-4)' }}><Skeleton width="50px" height={14} /></td>
    </tr>
  );
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="card card-padding">
      <Skeleton width="40%" height={18} style={{ marginBottom: 'var(--space-4)' }} />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={`${100 - i * 15}%`} height={13} style={{ marginBottom: 'var(--space-2)' }} />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="card" style={{ padding: 'var(--space-6)' }}>
      <Skeleton width="30%" height={18} style={{ marginBottom: 'var(--space-6)' }} />
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 180 }}>
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton
            key={i}
            width="100%"
            height={`${20 + Math.random() * 80}%`}
            borderRadius="var(--radius-sm)"
            style={{ flex: 1 }}
          />
        ))}
      </div>
    </div>
  );
}
