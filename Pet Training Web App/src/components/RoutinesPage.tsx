import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Plus, Play, Clock, Trash2 } from 'lucide-react';
import { generateMockRoutines } from '../lib/mockData';
import { toast } from 'sonner@2.0.3';
import { formatDistanceToNow } from 'date-fns';

export default function RoutinesPage() {
  const [routines, setRoutines] = useState(generateMockRoutines());

  const toggleRoutine = (id: string) => {
    setRoutines((prev) =>
      prev.map((r) => (r.id === id ? { ...r, enabled: !r.enabled } : r))
    );
  };

  const runRoutine = (name: string) => {
    toast.success(`${name} started`);
  };

  const deleteRoutine = (id: string) => {
    setRoutines((prev) => prev.filter((r) => r.id !== id));
    toast.success('Routine deleted');
  };

  const actionLabels = {
    pet: 'Pet',
    treat: 'Treat',
    play: 'Play',
    'sit-drill': 'Sit Drill',
    wait: 'Wait',
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2>Routines</h2>
            <p className="text-sm text-muted-foreground">Automated training sequences</p>
          </div>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Routine
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="space-y-3 max-w-3xl mx-auto">
          {routines.map((routine) => (
            <Card key={routine.id} className="p-5">
              <div className="flex items-start gap-4">
                <Switch
                  checked={routine.enabled}
                  onCheckedChange={() => toggleRoutine(routine.id)}
                  className="mt-1"
                />
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-base">{routine.name}</h3>
                    {routine.enabled && (
                      <Badge variant="secondary" className="text-xs">Active</Badge>
                    )}
                  </div>

                  {routine.schedule && (
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground mb-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{routine.schedule}</span>
                    </div>
                  )}

                  {routine.lastRun && (
                    <p className="text-xs text-muted-foreground mb-3">
                      Last run {formatDistanceToNow(routine.lastRun, { addSuffix: true })}
                    </p>
                  )}

                  <Separator className="my-3" />

                  <div className="flex items-center gap-2 flex-wrap">
                    {routine.steps.map((step, index) => (
                      <div key={step.id} className="flex items-center gap-1.5">
                        <Badge variant="outline" className="text-xs">
                          {actionLabels[step.action]}
                          {step.duration && ` · ${step.duration}s`}
                        </Badge>
                        {index < routine.steps.length - 1 && (
                          <span className="text-muted-foreground text-xs">→</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => runRoutine(routine.name)}
                  >
                    <Play className="w-3.5 h-3.5" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => deleteRoutine(routine.id)}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
