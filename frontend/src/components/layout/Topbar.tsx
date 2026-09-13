import React, { useState, useEffect, useCallback } from 'react';
import { Search, Bell, Sun, Moon, Menu, Github, X } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { SearchCommandPalette } from '../SearchCommandPalette';

export function Topbar() {
  const { sidebarCollapsed, setMobileSidebarOpen } = useApp();
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <>
      <header className={`topbar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Mobile menu */}
        <button
          className="btn btn-ghost btn-icon btn-sm"
          style={{ display: 'none' }}
          id="mobile-menu-btn"
          onClick={() => setMobileSidebarOpen(true)}
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>

        {/* Search */}
        <div
          className="topbar-search"
          onClick={() => setSearchOpen(true)}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && setSearchOpen(true)}
          aria-label="Open search"
        >
          <Search size={14} />
          <span style={{ flex: 1 }}>Search commits, repos, authors...</span>
          <div className="topbar-search-hint">
            <span className="kbd">⌘</span>
            <span className="kbd">K</span>
          </div>
        </div>

        {/* Actions */}
        <div className="topbar-actions">
          {/* GitHub status */}
          <div className="chip" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Github size={12} />
            <span className={`status-dot ${user?.githubConnected ? 'connected' : 'disconnected'}`} style={{ width: 6, height: 6 }} />
          </div>

          {/* Theme */}
          <button
            onClick={toggleTheme}
            className="btn btn-ghost btn-icon"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          {/* Notifications */}
          <div style={{ position: 'relative' }}>
            <button
              className="btn btn-ghost btn-icon"
              onClick={() => setNotifOpen(!notifOpen)}
              aria-label="Notifications"
            >
              <Bell size={18} />
              <span style={{
                position: 'absolute', top: 6, right: 6,
                width: 8, height: 8, background: 'var(--accent-primary)',
                borderRadius: '50%', border: '2px solid var(--bg-surface)',
              }} />
            </button>
          </div>

          {/* Avatar */}
          {user && (
            <img
              src={user.avatar}
              alt={user.login}
              className="avatar"
              style={{ width: 30, height: 30 }}
            />
          )}
        </div>
      </header>

      {searchOpen && (
        <SearchCommandPalette onClose={() => setSearchOpen(false)} />
      )}
    </>
  );
}
