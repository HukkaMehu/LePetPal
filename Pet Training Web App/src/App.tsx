import { useState } from 'react';
import { SidebarProvider } from './components/ui/sidebar';
import { AppSidebar } from './components/AppSidebar';
import { Toaster } from './components/ui/sonner';
import ErrorBoundary from './components/ErrorBoundary';
import ConnectionStatusBanner from './components/ConnectionStatusBanner';
import LivePage from './components/LivePage';
import GalleryPage from './components/GalleryPage';
import AnalyticsPage from './components/AnalyticsPage';
import RoutinesPage from './components/RoutinesPage';
import SettingsPage from './components/SettingsPage';
import TestPage from './components/TestPage';
import ActivityChat from './components/ActivityChat';

export default function App() {
  const [currentPage, setCurrentPage] = useState<'live' | 'gallery' | 'analytics' | 'routines' | 'settings' | 'tests' | 'chat'>('live');

  return (
    <ErrorBoundary>
      <SidebarProvider>
        <ConnectionStatusBanner />
        <div className="flex h-screen w-full bg-background">
          <AppSidebar currentPage={currentPage} onNavigate={setCurrentPage} />
          <main className="flex-1 overflow-hidden">
            {currentPage === 'live' && <LivePage />}
            {currentPage === 'gallery' && <GalleryPage />}
            {currentPage === 'analytics' && <AnalyticsPage />}
            {currentPage === 'routines' && <RoutinesPage />}
            {currentPage === 'settings' && <SettingsPage />}
            {currentPage === 'tests' && <TestPage />}
            {currentPage === 'chat' && <ActivityChat />}
          </main>
        </div>
        <Toaster />
      </SidebarProvider>
    </ErrorBoundary>
  );
}
