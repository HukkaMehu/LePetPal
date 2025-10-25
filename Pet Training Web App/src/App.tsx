import { useState } from 'react';
import { SidebarProvider } from './components/ui/sidebar';
import { AppSidebar } from './components/AppSidebar';
import { Toaster } from './components/ui/sonner';
import LivePage from './components/LivePage';
import GalleryPage from './components/GalleryPage';
import AnalyticsPage from './components/AnalyticsPage';
import RoutinesPage from './components/RoutinesPage';
import SettingsPage from './components/SettingsPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState<'live' | 'gallery' | 'analytics' | 'routines' | 'settings'>('live');

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-background">
        <AppSidebar currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="flex-1 overflow-hidden">
          {currentPage === 'live' && <LivePage />}
          {currentPage === 'gallery' && <GalleryPage />}
          {currentPage === 'analytics' && <AnalyticsPage />}
          {currentPage === 'routines' && <RoutinesPage />}
          {currentPage === 'settings' && <SettingsPage />}
        </main>
      </div>
      <Toaster />
    </SidebarProvider>
  );
}
