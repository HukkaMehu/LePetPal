import ConfigPanel from '@/components/ConfigPanel';
import VideoPanel from '@/components/VideoPanel';
import CommandBar from '@/components/CommandBar';
import StatusDisplay from '@/components/StatusDisplay';
import SSEProvider from '@/components/SSEProvider';

export default function Home() {
  return (
    <SSEProvider>
      <div className="min-h-screen bg-gray-50 p-4 sm:p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          <header className="mb-4 sm:mb-6">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">LePetPal</h1>
            <p className="text-sm sm:text-base text-gray-600 mt-1">AI-powered pet robotics control</p>
          </header>

          {/* Mobile: Stack vertically (<768px) */}
          {/* Desktop: Side-by-side (≥768px) */}
          <div className="flex flex-col md:flex-row gap-4 sm:gap-6">
            {/* Left column - Video and Config */}
            <div className="flex-1 md:flex-[2] space-y-4 sm:space-y-6">
              <VideoPanel />
              <ConfigPanel />
            </div>

            {/* Right column - Commands and Status */}
            <div className="flex-1 md:flex-[1] space-y-4 sm:space-y-6">
              <CommandBar />
              <StatusDisplay />
            </div>
          </div>
        </div>
      </div>
    </SSEProvider>
  );
}
