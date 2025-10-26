import { Button } from './ui/button';
import { Heart, Cookie, Play, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { useState } from 'react';

const BACKEND_URL = 'https://lepetpal.verkkoventure.com';

interface ActionPanelProps {
  isOnline: boolean;
}

export default function ActionPanel({ isOnline }: ActionPanelProps) {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');

  const handleAction = async (action: string, label: string) => {
    if (!isOnline) {
      toast.error('Device offline', {
        description: 'Cannot send command when device is disconnected',
      });
      return;
    }

    // Map actions to backend commands
    const commandMap: { [key: string]: number } = {
      'pet': 0,           // Pet action
      'fetch': 1,         // Fetch/throw action
      'take-control': 2,  // Take control action
    };

    const command = commandMap[action];
    if (command === undefined) {
      // For unmapped actions, show a placeholder message
      setActiveAction(action);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setActiveAction(null);
      toast.success(`${label} command sent`, {
        description: 'Your pet will love this!',
      });
      return;
    }

    setActiveAction(action);
    setStatusMessage('Sending command...');

    try {
      const response = await fetch(`${BACKEND_URL}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Command accepted:', data.request_id);

      toast.success(`${label} command sent`, {
        description: `Request ID: ${data.request_id}`,
      });

      // Poll status
      const checkStatus = setInterval(async () => {
        try {
          const statusRes = await fetch(`${BACKEND_URL}/status/${data.request_id}`);
          const status = await statusRes.json();

          const progressText = status.progress ? ` (${status.progress}%)` : '';
          setStatusMessage(`${status.state}: ${status.message}${progressText}`);

          if (status.state === 'succeeded') {
            clearInterval(checkStatus);
            setActiveAction(null);
            setStatusMessage('');
            toast.success(`${label} completed!`, {
              description: 'Action finished successfully',
            });
          } else if (status.state === 'failed') {
            clearInterval(checkStatus);
            setActiveAction(null);
            setStatusMessage('');
            toast.error(`${label} failed`, {
              description: status.message,
            });
          }
        } catch (error) {
          console.error('Status check failed:', error);
          clearInterval(checkStatus);
          setActiveAction(null);
          setStatusMessage('');
        }
      }, 1000);
    } catch (error) {
      console.error('Command failed:', error);
      setActiveAction(null);
      setStatusMessage('');
      toast.error(`${label} failed`, {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  const actions = [
    {
      id: 'pet',
      label: 'Pet',
      icon: Heart,
      description: 'Gentle petting motion',
      color: 'bg-pink-500 hover:bg-pink-600 text-white',
    },
    {
      id: 'take-control',
      label: 'Take-control',
      icon: Cookie,
      description: 'Dispense a treat',
      color: 'bg-amber-500 hover:bg-amber-600 text-white',
    },
    {
      id: 'fetch',
      label: 'Fetch',
      icon: Play,
      description: 'Launch fetch toy',
      color: 'bg-blue-500 hover:bg-blue-600 text-white',
    },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-neutral-900">Quick Actions</h3>
        <div className="text-xs text-neutral-500">
          {isOnline ? 'Device ready' : 'Device offline'}
        </div>
      </div>

      {statusMessage && (
        <div className="text-xs text-neutral-600 bg-neutral-100 p-2 rounded">
          {statusMessage}
        </div>
      )}

      <div className="space-y-2">
        {actions.map(({ id, label, icon: Icon, description, color }) => (
          <Button
            key={id}
            onClick={() => handleAction(id, label)}
            disabled={!isOnline || activeAction !== null}
            className={`w-full h-auto flex flex-col items-start p-4 ${isOnline ? color : 'bg-neutral-200 text-neutral-400'
              }`}
          >
            <div className="flex items-center gap-2 w-full">
              {activeAction === id ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Icon className="w-5 h-5" />
              )}
              <span className="font-medium">{label}</span>
            </div>
            <span className="text-xs opacity-90 mt-1">{description}</span>
          </Button>
        ))}
      </div>

      {!isOnline && (
        <div className="text-xs text-neutral-500 text-center p-2 bg-neutral-100 rounded">
          Reconnecting to device...
        </div>
      )}
    </div>
  );
}
