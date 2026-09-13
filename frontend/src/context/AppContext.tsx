import React, { createContext, useContext, useState, type ReactNode } from 'react';
import type { Repository } from '../types';

interface AppContextValue {
  selectedRepository: Repository | null;
  setSelectedRepository: (repo: Repository | null) => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (v: boolean) => void;
  mobileSidebarOpen: boolean;
  setMobileSidebarOpen: (v: boolean) => void;
  demoMode: boolean;
  setDemoMode: (v: boolean) => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [selectedRepository, setSelectedRepository] = useState<Repository | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [demoMode, setDemoMode] = useState(false);

  return (
    <AppContext.Provider value={{
      selectedRepository, setSelectedRepository,
      sidebarCollapsed, setSidebarCollapsed,
      mobileSidebarOpen, setMobileSidebarOpen,
      demoMode, setDemoMode,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
