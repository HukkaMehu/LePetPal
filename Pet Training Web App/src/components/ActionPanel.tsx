import { Button } from './ui/button';
import { Heart, Cookie, Play, Loader2 } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { useState } from 'react';

interface ActionPanelProps {
  isOnline: boolean;
}

export default function ActionPanel({ isOnline }: ActionPanelProps) {
  const [activeAction, setActiveAction] = useState<string | null>(null);

  const handleAction = async (action: string, label: string) => {
    if (!isOnline) {
      toast.error('Device offline', {
        description: 'Cannot send command when device is disconnected',
      });
      return;
    }

    setActiveAction(action);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setActiveAction(null);
    toast.success(`${label} command sent`, {
      description: 'Your pet will love this!',
    });
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
      id: 'treat',
      label: 'Treat',
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

      <div className="space-y-2">
        {actions.map(({ id, label, icon: Icon, description, color }) => (
          <Button
            key={id}
            onClick={() => handleAction(id, label)}
            disabled={!isOnline || activeAction !== null}
            className={`w-full h-auto flex flex-col items-start p-4 ${
              isOnline ? color : 'bg-neutral-200 text-neutral-400'
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
