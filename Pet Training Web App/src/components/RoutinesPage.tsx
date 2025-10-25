import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from './ui/alert-dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Plus, Play, Clock, Trash2, Edit2, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import { useRoutines } from '../hooks/useRoutines';
import { Routine, RoutineCreate, RoutineUpdate, RoutineActionType } from '../types';
import { RoutinesSkeleton } from './LoadingStates';
import { FieldError } from './FormError';

interface RoutineStepForm {
  action: RoutineActionType;
  duration?: number;
  repeat?: number;
}

interface RoutineFormData {
  name: string;
  schedule: string;
  enabled: boolean;
  steps: RoutineStepForm[];
}

export default function RoutinesPage() {
  const { routines, loading, error, createRoutine, updateRoutine, deleteRoutine, triggerRoutine, lastNotification } = useRoutines();
  
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingRoutine, setEditingRoutine] = useState<Routine | null>(null);
  const [deleteConfirmRoutine, setDeleteConfirmRoutine] = useState<Routine | null>(null);
  const [formData, setFormData] = useState<RoutineFormData>({
    name: '',
    schedule: '',
    enabled: true,
    steps: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [triggeringRoutineId, setTriggeringRoutineId] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<{ name?: string; schedule?: string; steps?: string }>({});

  // Action labels for display
  const actionLabels: Record<RoutineActionType, string> = {
    pet: 'Pet',
    treat: 'Treat',
    play: 'Play',
    'sit-drill': 'Sit Drill',
    wait: 'Wait',
    fetch: 'Fetch',
  };

  // Available actions for the select dropdown
  const availableActions: RoutineActionType[] = ['pet', 'treat', 'play', 'sit-drill', 'wait', 'fetch'];

  // Reset form data
  const resetForm = () => {
    setFormData({
      name: '',
      schedule: '',
      enabled: true,
      steps: [],
    });
    setFormErrors({});
  };

  // Open create dialog
  const handleOpenCreateDialog = () => {
    resetForm();
    setEditingRoutine(null);
    setIsCreateDialogOpen(true);
  };

  // Open edit dialog
  const handleOpenEditDialog = (routine: Routine) => {
    setEditingRoutine(routine);
    setFormData({
      name: routine.name,
      schedule: routine.schedule || '',
      enabled: routine.enabled,
      steps: routine.steps.map(step => ({
        action: step.action,
        duration: step.duration,
        repeat: step.repeat,
      })),
    });
    setIsCreateDialogOpen(true);
  };

  // Close dialog
  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
    setEditingRoutine(null);
    resetForm();
  };

  // Add step to form
  const handleAddStep = () => {
    setFormData(prev => ({
      ...prev,
      steps: [...prev.steps, { action: 'pet', duration: 5 }],
    }));
  };

  // Remove step from form
  const handleRemoveStep = (index: number) => {
    setFormData(prev => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index),
    }));
  };

  // Update step in form
  const handleUpdateStep = (index: number, field: keyof RoutineStepForm, value: any) => {
    setFormData(prev => ({
      ...prev,
      steps: prev.steps.map((step, i) => 
        i === index ? { ...step, [field]: value } : step
      ),
    }));
  };

  // Validate form
  const validateForm = (): boolean => {
    const errors: { name?: string; schedule?: string; steps?: string } = {};

    if (!formData.name.trim()) {
      errors.name = 'Routine name is required';
    }

    if (formData.steps.length === 0) {
      errors.steps = 'At least one step is required';
    }

    // Validate cron expression if provided (basic validation)
    if (formData.schedule && formData.schedule.trim()) {
      const cronParts = formData.schedule.trim().split(' ');
      if (cronParts.length !== 5) {
        errors.schedule = 'Invalid schedule format. Use cron format: "minute hour day month weekday"';
      }
    }

    setFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      toast.error('Please fix the form errors');
      return false;
    }

    return true;
  };

  // Handle form submit (create or update)
  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      const routineData: RoutineCreate | RoutineUpdate = {
        name: formData.name,
        schedule: formData.schedule || undefined,
        enabled: formData.enabled,
        steps: formData.steps,
      };

      if (editingRoutine) {
        // Update existing routine
        await updateRoutine(editingRoutine.id, routineData);
        toast.success('Routine updated successfully');
      } else {
        // Create new routine
        await createRoutine(routineData as RoutineCreate);
        toast.success('Routine created successfully');
      }

      handleCloseDialog();
    } catch (err) {
      console.error('Error saving routine:', err);
      toast.error(editingRoutine ? 'Failed to update routine' : 'Failed to create routine');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Toggle routine enabled/disabled
  const handleToggleRoutine = async (routine: Routine) => {
    try {
      await updateRoutine(routine.id, { enabled: !routine.enabled });
      toast.success(routine.enabled ? 'Routine disabled' : 'Routine enabled');
    } catch (err) {
      console.error('Error toggling routine:', err);
      toast.error('Failed to toggle routine');
    }
  };

  // Trigger routine manually
  const handleTriggerRoutine = async (routine: Routine) => {
    setTriggeringRoutineId(routine.id);
    try {
      await triggerRoutine(routine.id);
      toast.success(`${routine.name} started`);
    } catch (err) {
      console.error('Error triggering routine:', err);
      toast.error('Failed to start routine');
    } finally {
      setTriggeringRoutineId(null);
    }
  };

  // Confirm and delete routine
  const handleDeleteRoutine = async () => {
    if (!deleteConfirmRoutine) return;

    try {
      await deleteRoutine(deleteConfirmRoutine.id);
      toast.success('Routine deleted');
      setDeleteConfirmRoutine(null);
    } catch (err) {
      console.error('Error deleting routine:', err);
      toast.error('Failed to delete routine');
    }
  };

  // Listen for WebSocket routine notifications and show toast
  useEffect(() => {
    if (lastNotification) {
      if (lastNotification.status === 'started') {
        toast.info(`${lastNotification.routineName} started`);
      } else if (lastNotification.status === 'completed') {
        toast.success(`${lastNotification.routineName} completed`);
      }
    }
  }, [lastNotification]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2>Routines</h2>
            <p className="text-sm text-muted-foreground">Automated training sequences</p>
          </div>
          <Button onClick={handleOpenCreateDialog}>
            <Plus className="w-4 h-4 mr-2" />
            New Routine
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading && (
          <div className="max-w-3xl mx-auto">
            <RoutinesSkeleton />
          </div>
        )}

        {error && (
          <div className="text-center text-destructive py-8">
            Error loading routines: {error.message}
          </div>
        )}

        {!loading && !error && routines.length === 0 && (
          <div className="text-center text-muted-foreground py-8">
            No routines yet. Create your first routine to get started!
          </div>
        )}

        {!loading && !error && routines.length > 0 && (
          <div className="space-y-3 max-w-3xl mx-auto">
            {routines.map((routine) => (
              <Card key={routine.id} className="p-5">
                <div className="flex items-start gap-4">
                  <Switch
                    checked={routine.enabled}
                    onCheckedChange={() => handleToggleRoutine(routine)}
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
                      onClick={() => handleTriggerRoutine(routine)}
                      disabled={triggeringRoutineId === routine.id}
                      title="Run routine now"
                    >
                      {triggeringRoutineId === routine.id ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Play className="w-3.5 h-3.5" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleOpenEditDialog(routine)}
                      title="Edit routine"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setDeleteConfirmRoutine(routine)}
                      title="Delete routine"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={handleCloseDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingRoutine ? 'Edit Routine' : 'Create New Routine'}</DialogTitle>
            <DialogDescription>
              {editingRoutine 
                ? 'Update the routine details below' 
                : 'Create a new automated training routine'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Routine Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Routine Name</Label>
              <Input
                id="name"
                placeholder="e.g., Morning Training"
                value={formData.name}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, name: e.target.value }));
                  if (formErrors.name) setFormErrors(prev => ({ ...prev, name: undefined }));
                }}
                className={formErrors.name ? 'border-destructive' : ''}
              />
              <FieldError error={formErrors.name} />
            </div>

            {/* Schedule (Cron) */}
            <div className="space-y-2">
              <Label htmlFor="schedule">Schedule (Optional)</Label>
              <Input
                id="schedule"
                placeholder="e.g., 0 9 * * * (9 AM daily)"
                value={formData.schedule}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, schedule: e.target.value }));
                  if (formErrors.schedule) setFormErrors(prev => ({ ...prev, schedule: undefined }));
                }}
                className={formErrors.schedule ? 'border-destructive' : ''}
              />
              {!formErrors.schedule && (
                <p className="text-xs text-muted-foreground">
                  Use cron format: minute hour day month weekday
                </p>
              )}
              <FieldError error={formErrors.schedule} />
            </div>

            {/* Enabled Toggle */}
            <div className="flex items-center gap-2">
              <Switch
                id="enabled"
                checked={formData.enabled}
                onCheckedChange={(checked: boolean) => setFormData(prev => ({ ...prev, enabled: checked }))}
              />
              <Label htmlFor="enabled">Enable routine</Label>
            </div>

            {/* Steps */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Steps</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    handleAddStep();
                    if (formErrors.steps) setFormErrors(prev => ({ ...prev, steps: undefined }));
                  }}
                >
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  Add Step
                </Button>
              </div>

              {formData.steps.length === 0 && !formErrors.steps && (
                <p className="text-sm text-muted-foreground">No steps added yet</p>
              )}
              <FieldError error={formErrors.steps} />

              <div className="space-y-2">
                {formData.steps.map((step, index) => (
                  <Card key={index} className="p-3">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-muted-foreground">
                        {index + 1}
                      </span>

                      <div className="flex-1 grid grid-cols-2 gap-2">
                        <div className="space-y-1">
                          <Label className="text-xs">Action</Label>
                          <Select
                            value={step.action}
                            onValueChange={(value: string) => handleUpdateStep(index, 'action', value as RoutineActionType)}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {availableActions.map(action => (
                                <SelectItem key={action} value={action}>
                                  {actionLabels[action]}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-1">
                          <Label className="text-xs">Duration (seconds)</Label>
                          <Input
                            type="number"
                            min="1"
                            value={step.duration || ''}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleUpdateStep(index, 'duration', parseInt(e.target.value) || undefined)}
                            placeholder="Optional"
                          />
                        </div>
                      </div>

                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveStep(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : editingRoutine ? 'Update Routine' : 'Create Routine'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteConfirmRoutine} onOpenChange={() => setDeleteConfirmRoutine(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Routine</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteConfirmRoutine?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteRoutine}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
