import { Badge } from './ui/badge';
import { Box, Activity, Target, Flame } from 'lucide-react';

interface OverlayTogglesProps {
  overlays: {
    dogBox: boolean;
    keypoints: boolean;
    objects: boolean;
    heatmap: boolean;
  };
  onChange: (key: keyof OverlayTogglesProps['overlays']) => void;
}

export default function OverlayToggles({ overlays, onChange }: OverlayTogglesProps) {
  const toggles = [
    {
      key: 'dogBox' as const,
      label: 'Dog Box',
      icon: Box,
      color: 'border-green-400 bg-green-50 text-green-700 hover:bg-green-100',
    },
    {
      key: 'keypoints' as const,
      label: 'Keypoints',
      icon: Activity,
      color: 'border-blue-400 bg-blue-50 text-blue-700 hover:bg-blue-100',
    },
    {
      key: 'objects' as const,
      label: 'Objects',
      icon: Target,
      color: 'border-yellow-400 bg-yellow-50 text-yellow-700 hover:bg-yellow-100',
    },
    {
      key: 'heatmap' as const,
      label: 'Motion Heatmap',
      icon: Flame,
      color: 'border-orange-400 bg-orange-50 text-orange-700 hover:bg-orange-100',
    },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {toggles.map(({ key, label, icon: Icon, color }) => (
        <button
          key={key}
          onClick={() => onChange(key)}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border-2 transition-all cursor-pointer ${
            overlays[key]
              ? color
              : 'border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50'
          }`}
        >
          <Icon className="w-3.5 h-3.5" />
          <span className="text-sm">{label}</span>
        </button>
      ))}
    </div>
  );
}
