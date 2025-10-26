import { Card } from './ui/card';
import { Sparkles, X } from 'lucide-react';
import { Button } from './ui/button';
import { useState } from 'react';

interface Tip {
  id: string;
  title: string;
  message: string;
  confidence: number;
}

export default function CoachTips() {
  const [tips, setTips] = useState<Tip[]>([
    {
      id: '1',
      title: 'Great sitting streak!',
      message: 'Your dog has successfully sat 8 times in the last hour. Consider a reward routine.',
      confidence: 0.92,
    },
    {
      id: '2',
      title: 'Active period detected',
      message: 'High activity between 2-4 PM. Good time to schedule fetch training.',
      confidence: 0.87,
    },
    {
      id: '3',
      title: 'Calm behavior',
      message: 'Your dog has been calm for 20 minutes. Perfect opportunity for a gentle pet.',
      confidence: 0.94,
    },
  ]);

  const dismissTip = (id: string) => {
    setTips(tips.filter(tip => tip.id !== id));
  };

  if (tips.length === 0) {
    return (
      <Card className="p-4 bg-neutral-50 border-neutral-200">
        <div className="flex items-center gap-2 text-neutral-500">
          <Sparkles className="w-4 h-4" />
          <span className="text-sm">No new coaching tips</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-2">
      {tips.map((tip) => (
        <Card
          key={tip.id}
          className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 relative"
        >
          <Button
            size="sm"
            variant="ghost"
            className="absolute top-2 right-2 h-6 w-6 p-0 hover:bg-white/50"
            onClick={() => dismissTip(tip.id)}
          >
            <X className="w-3 h-3" />
          </Button>
          
          <div className="flex items-start gap-3 pr-8">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-sm text-neutral-900">{tip.title}</h4>
                <span className="text-xs text-neutral-500">
                  {Math.round(tip.confidence * 100)}%
                </span>
              </div>
              <p className="text-sm text-neutral-700">{tip.message}</p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
