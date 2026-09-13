import React, { type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useApp } from '../../context/AppContext';

export function AppShell({ children }: { children: ReactNode }) {
  const { sidebarCollapsed } = useApp();
  return (
    <div className="app-shell">
      <Sidebar />
      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Topbar />
        <main className="page-wrapper">
          {children}
        </main>
      </div>
    </div>
  );
}
