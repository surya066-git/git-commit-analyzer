import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, GitBranch, GitCommit, History,
  BarChart3, Users, Lightbulb, Activity, Settings,
  ChevronLeft, ChevronRight, Github, Cpu, FlaskConical
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { label: 'Overview',      to: '/dashboard',     icon: LayoutDashboard },
  { label: 'Repositories',  to: '/repositories',  icon: GitBranch },
  { label: 'Commit Analyzer', to: '/analyzer',    icon: GitCommit },
  { label: 'Commit History', to: '/history',      icon: History },
  { label: 'Analytics',     to: '/analytics',     icon: BarChart3 },
  { label: 'Contributors',  to: '/contributors',  icon: Users },
  { label: 'Recommendations', to: '/recommendations', icon: Lightbulb, badge: 4 },
  { label: 'Activity',      to: '/activity',      icon: Activity },
];

const BOTTOM_NAV_ITEMS = [
  { label: 'Model Performance', to: '/model-performance', icon: FlaskConical },
  { label: 'Settings',         to: '/settings',           icon: Settings },
];

export function Sidebar() {
  const { sidebarCollapsed, setSidebarCollapsed, mobileSidebarOpen, setMobileSidebarOpen } = useApp();
  const { user } = useAuth();
  const location = useLocation();

  const collapsed = sidebarCollapsed;

  const Tooltip = ({ label, children }: { label: string; children: React.ReactNode }) => (
    <div className="tooltip-wrapper">
      {children}
      {collapsed && <span className="tooltip-text">{label}</span>}
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileSidebarOpen && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 499 }}
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileSidebarOpen ? 'mobile-open' : ''}`}>
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-mark" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="7" cy="12" r="3" fill="white"/>
              <circle cx="17" cy="6" r="3" fill="white" opacity="0.8"/>
              <circle cx="17" cy="18" r="3" fill="white" opacity="0.8"/>
              <line x1="10" y1="10.5" x2="14" y2="7.5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              <line x1="10" y1="13.5" x2="14" y2="16.5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
          {!collapsed && (
            <span className="logo-text">Commit<span>IQ</span></span>
          )}
          <button
            onClick={() => setSidebarCollapsed(!collapsed)}
            className="btn btn-ghost btn-icon btn-sm"
            style={{ marginLeft: 'auto', flexShrink: 0 }}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav" aria-label="Main navigation">
          {!collapsed && <div className="nav-section-label">Navigation</div>}

          {NAV_ITEMS.map(item => (
            <Tooltip key={item.to} label={item.label}>
              <NavLink
                to={item.to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                aria-current={location.pathname.startsWith(item.to) ? 'page' : undefined}
              >
                <span className="nav-item-icon"><item.icon size={18} /></span>
                <span className="nav-item-label">{item.label}</span>
                {item.badge && <span className="nav-item-badge">{item.badge}</span>}
              </NavLink>
            </Tooltip>
          ))}

          {!collapsed && <div className="nav-section-label" style={{ marginTop: 'var(--space-4)' }}>Tools</div>}
          {BOTTOM_NAV_ITEMS.map(item => (
            <Tooltip key={item.to} label={item.label}>
              <NavLink
                to={item.to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <span className="nav-item-icon"><item.icon size={18} /></span>
                <span className="nav-item-label">{item.label}</span>
              </NavLink>
            </Tooltip>
          ))}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="github-status">
            <span className={`status-dot ${user?.githubConnected ? 'connected' : 'disconnected'}`} />
            {!collapsed && (
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                {user?.githubConnected ? 'GitHub connected' : 'GitHub disconnected'}
              </span>
            )}
          </div>
          {user && !collapsed && (
            <div className="flex items-center gap-2" style={{ padding: 'var(--space-2) var(--space-3)' }}>
              <img src={user.avatar} alt={user.login} className="avatar" style={{ width: 24, height: 24 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user.name || user.login}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  @{user.login}
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
