import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, GitCommit, GitBranch, Users, FileCode } from 'lucide-react';
import { DEMO_COMMITS, DEMO_REPOSITORY, DEMO_CONTRIBUTORS } from '../services/demoData';
import { CategoryBadge } from './ui/CategoryBadge';
import { useApp } from '../context/AppContext';

interface SearchCommandPaletteProps {
  onClose: () => void;
}

export function SearchCommandPalette({ onClose }: SearchCommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { demoMode } = useApp();

  useEffect(() => {
    inputRef.current?.focus();
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const commits = query.length > 1
    ? DEMO_COMMITS.filter(c =>
        c.message.toLowerCase().includes(query.toLowerCase()) ||
        c.commitHash.includes(query.toLowerCase()) ||
        c.author.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5)
    : DEMO_COMMITS.slice(0, 3);

  const repos = query.length > 1
    ? [DEMO_REPOSITORY].filter(r => r.name.toLowerCase().includes(query.toLowerCase()))
    : [DEMO_REPOSITORY];

  const contributors = query.length > 1
    ? DEMO_CONTRIBUTORS.filter(c => c.login.toLowerCase().includes(query.toLowerCase()) || (c.name || '').toLowerCase().includes(query.toLowerCase()))
    : DEMO_CONTRIBUTORS.slice(0, 2);

  const allItems = [
    ...repos.map(r => ({ type: 'repo', item: r, key: `repo-${r.id}` })),
    ...commits.map(c => ({ type: 'commit', item: c, key: `commit-${c.commitHash}` })),
    ...contributors.map(c => ({ type: 'contributor', item: c, key: `contrib-${c.id}` })),
  ];

  const handleNavigate = (item: typeof allItems[0]) => {
    if (item.type === 'commit') navigate(`/commits/${(item.item as typeof DEMO_COMMITS[0]).commitHash}`);
    if (item.type === 'repo') navigate('/repositories');
    if (item.type === 'contributor') navigate('/contributors');
    onClose();
  };

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={e => e.stopPropagation()} role="dialog" aria-label="Search">
        <div className="command-input-wrapper">
          <Search size={18} color="var(--text-tertiary)" />
          <input
            ref={inputRef}
            className="command-input"
            placeholder="Search commits, repositories, authors, files..."
            value={query}
            onChange={e => { setQuery(e.target.value); setSelected(0); }}
            aria-label="Search query"
          />
          {query && (
            <button onClick={() => setQuery('')} className="btn btn-ghost btn-icon btn-sm">
              <span style={{ fontSize: 12 }}>✕</span>
            </button>
          )}
        </div>

        <div className="command-results">
          {repos.length > 0 && (
            <>
              <div className="command-section-label">Repositories</div>
              {repos.map((repo, i) => (
                <div
                  key={repo.id}
                  className="command-item"
                  onClick={() => handleNavigate({ type: 'repo', item: repo, key: `repo-${repo.id}` })}
                >
                  <GitBranch size={16} color="var(--text-tertiary)" />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-primary)' }}>{repo.fullName}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>{repo.language} • {repo.stars} stars</div>
                  </div>
                </div>
              ))}
            </>
          )}

          {commits.length > 0 && (
            <>
              <div className="command-section-label">Commits</div>
              {commits.map(commit => (
                <div
                  key={commit.commitHash}
                  className="command-item"
                  onClick={() => handleNavigate({ type: 'commit', item: commit, key: `commit-${commit.commitHash}` })}
                >
                  <GitCommit size={16} color="var(--text-tertiary)" />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {commit.message}
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{commit.commitHash}</span> • {commit.author}
                    </div>
                  </div>
                  <CategoryBadge category={commit.category} size="sm" />
                </div>
              ))}
            </>
          )}

          {contributors.length > 0 && (
            <>
              <div className="command-section-label">Contributors</div>
              {contributors.map(c => (
                <div
                  key={c.id}
                  className="command-item"
                  onClick={() => handleNavigate({ type: 'contributor', item: c, key: `contrib-${c.id}` })}
                >
                  <img src={c.avatar} alt={c.login} style={{ width: 20, height: 20, borderRadius: '50%' }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 'var(--text-sm)', fontWeight: 500, color: 'var(--text-primary)' }}>{c.name || c.login}</div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>{c.totalCommits} commits • avg quality: {c.averageQuality}/100</div>
                  </div>
                </div>
              ))}
            </>
          )}

          {allItems.length === 0 && (
            <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 'var(--text-sm)' }}>
              No matching results for "{query}"
            </div>
          )}
        </div>

        <div className="command-footer">
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>Press</span>
          <span className="kbd">Esc</span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>to close</span>
        </div>
      </div>
    </div>
  );
}
