import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Separator } from './ui/separator';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Video, Shield, Bell, Cpu, Wifi, WifiOff, Activity } from 'lucide-react';
import { toast } from 'sonner';
import { useModels, useSystemStatus } from '../hooks';
import { SettingsSkeleton } from './LoadingStates';

export default function SettingsPage() {
  // Hooks
  const { availableModels, activeModels, loading: modelsLoading, switchModels } = useModels();
  const { status, loading: statusLoading } = useSystemStatus();

  // Local state for model selection
  const [selectedDetector, setSelectedDetector] = useState<string>('');
  const [selectedActionRecognizer, setSelectedActionRecognizer] = useState<string>('');
  const [selectedPoseEstimator, setSelectedPoseEstimator] = useState<string>('');
  const [selectedPolicy, setSelectedPolicy] = useState<string>('');
  
  // Local state for video streaming
  const [streamProtocol, setStreamProtocol] = useState<'mjpeg' | 'webrtc'>('mjpeg');
  
  // Other settings
  const [faceBlur, setFaceBlur] = useState(false);
  const [notifications, setNotifications] = useState(true);

  // Sync active models to local state when they load
  useEffect(() => {
    if (activeModels) {
      setSelectedDetector(activeModels.detector || '');
      setSelectedActionRecognizer(activeModels.action_recognizer || '');
      setSelectedPoseEstimator(activeModels.pose_estimator || '');
      setSelectedPolicy(activeModels.policy || '');
    }
  }, [activeModels]);

  // Sync video stream type from status
  useEffect(() => {
    if (status?.video) {
      setStreamProtocol(status.video);
    }
  }, [status?.video]);

  // Get models by type
  const detectorModels = availableModels.filter(m => m.type === 'detector');
  const actionRecognizerModels = availableModels.filter(m => m.type === 'action_recognizer');
  const poseEstimatorModels = availableModels.filter(m => m.type === 'pose_estimator');
  const policyModels = availableModels.filter(m => m.type === 'policy');

  const handleSwitchModels = async () => {
    try {
      const request: any = {};
      
      // Only include models that have changed
      if (selectedDetector && selectedDetector !== activeModels.detector) {
        request.detector = selectedDetector;
      }
      if (selectedActionRecognizer && selectedActionRecognizer !== activeModels.action_recognizer) {
        request.actionRecognizer = selectedActionRecognizer;
      }
      if (selectedPoseEstimator && selectedPoseEstimator !== activeModels.pose_estimator) {
        request.poseEstimator = selectedPoseEstimator;
      }
      if (selectedPolicy && selectedPolicy !== activeModels.policy) {
        request.policy = selectedPolicy;
      }

      if (Object.keys(request).length === 0) {
        toast.info('No model changes to apply');
        return;
      }

      const response = await switchModels(request);
      
      if (response.success) {
        toast.success(response.message || 'Models switched successfully');
      } else {
        toast.error(response.message || 'Failed to switch models');
      }
    } catch (error) {
      console.error('Error switching models:', error);
      toast.error('Failed to switch models. Please try again.');
    }
  };

  const handleSave = () => {
    toast.success('Settings saved');
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div>
          <h2>Settings</h2>
          <p className="text-sm text-muted-foreground">Configure your preferences</p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl space-y-6">
          {/* Device Status */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                {status?.device === 'connected' ? (
                  <Wifi className="w-5 h-5 text-green-500" />
                ) : (
                  <WifiOff className="w-5 h-5 text-muted-foreground" />
                )}
              </div>
              <div>
                <h3>Device Status</h3>
                <p className="text-sm text-muted-foreground">
                  {statusLoading ? 'Loading...' : status?.device === 'connected' ? 'Connected' : 'Offline'}
                </p>
              </div>
            </div>

            {status && (
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">Connection Status</span>
                  <span className={`text-sm font-medium ${status.device === 'connected' ? 'text-green-500' : 'text-muted-foreground'}`}>
                    {status.device === 'connected' ? 'Connected' : 'Offline'}
                  </span>
                </div>
                <Separator />
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">Video Stream</span>
                  <span className="text-sm font-medium">{status.video?.toUpperCase() || 'N/A'}</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">FPS</span>
                  <span className="text-sm font-medium">{status.fps || 0}</span>
                </div>
                <Separator />
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">Latency</span>
                  <span className="text-sm font-medium">{status.latencyMs || 0} ms</span>
                </div>
              </div>
            )}
          </Card>

          {/* AI Models */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Cpu className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <h3>AI Models</h3>
                <p className="text-sm text-muted-foreground">Configure active models</p>
              </div>
            </div>

            {modelsLoading ? (
              <div className="flex items-center justify-center py-8">
                <Activity className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="space-y-4">
                {/* Detector Model */}
                {detectorModels.length > 0 && (
                  <div className="space-y-2">
                    <Label>Detector Model</Label>
                    <Select value={selectedDetector} onValueChange={setSelectedDetector}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select detector model" />
                      </SelectTrigger>
                      <SelectContent>
                        {detectorModels.map(model => (
                          <SelectItem key={model.name} value={model.name}>
                            {model.name} {model.version && `(${model.version})`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {detectorModels.find(m => m.name === selectedDetector)?.description && (
                      <p className="text-xs text-muted-foreground">
                        {detectorModels.find(m => m.name === selectedDetector)?.description}
                      </p>
                    )}
                  </div>
                )}

                {/* Action Recognizer Model */}
                {actionRecognizerModels.length > 0 && (
                  <div className="space-y-2">
                    <Label>Action Recognizer Model</Label>
                    <Select value={selectedActionRecognizer} onValueChange={setSelectedActionRecognizer}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select action recognizer model" />
                      </SelectTrigger>
                      <SelectContent>
                        {actionRecognizerModels.map(model => (
                          <SelectItem key={model.name} value={model.name}>
                            {model.name} {model.version && `(${model.version})`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {actionRecognizerModels.find(m => m.name === selectedActionRecognizer)?.description && (
                      <p className="text-xs text-muted-foreground">
                        {actionRecognizerModels.find(m => m.name === selectedActionRecognizer)?.description}
                      </p>
                    )}
                  </div>
                )}

                {/* Pose Estimator Model */}
                {poseEstimatorModels.length > 0 && (
                  <div className="space-y-2">
                    <Label>Pose Estimator Model</Label>
                    <Select value={selectedPoseEstimator} onValueChange={setSelectedPoseEstimator}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select pose estimator model" />
                      </SelectTrigger>
                      <SelectContent>
                        {poseEstimatorModels.map(model => (
                          <SelectItem key={model.name} value={model.name}>
                            {model.name} {model.version && `(${model.version})`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {poseEstimatorModels.find(m => m.name === selectedPoseEstimator)?.description && (
                      <p className="text-xs text-muted-foreground">
                        {poseEstimatorModels.find(m => m.name === selectedPoseEstimator)?.description}
                      </p>
                    )}
                  </div>
                )}

                {/* Policy Model */}
                {policyModels.length > 0 && (
                  <div className="space-y-2">
                    <Label>Policy Model</Label>
                    <Select value={selectedPolicy} onValueChange={setSelectedPolicy}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select policy model" />
                      </SelectTrigger>
                      <SelectContent>
                        {policyModels.map(model => (
                          <SelectItem key={model.name} value={model.name}>
                            {model.name} {model.version && `(${model.version})`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {policyModels.find(m => m.name === selectedPolicy)?.description && (
                      <p className="text-xs text-muted-foreground">
                        {policyModels.find(m => m.name === selectedPolicy)?.description}
                      </p>
                    )}
                  </div>
                )}

                {availableModels.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No models available
                  </p>
                )}

                {availableModels.length > 0 && (
                  <Button onClick={handleSwitchModels} className="w-full">
                    Apply Model Changes
                  </Button>
                )}
              </div>
            )}
          </Card>

          {/* Camera & Stream */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Video className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <h3>Camera & Stream</h3>
                <p className="text-sm text-muted-foreground">Video streaming settings</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Stream Protocol</Label>
                <Select value={streamProtocol} onValueChange={(value: 'mjpeg' | 'webrtc') => setStreamProtocol(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="webrtc">WebRTC (Low Latency)</SelectItem>
                    <SelectItem value="mjpeg">MJPEG (Compatible)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Current: {status?.video?.toUpperCase() || 'Not connected'}
                </p>
              </div>

              {status && (
                <>
                  <Separator />
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Current FPS</span>
                      <span className="text-sm font-medium">{status.fps || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Latency</span>
                      <span className="text-sm font-medium">{status.latencyMs || 0} ms</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </Card>

          {/* Privacy */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Shield className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <h3>Privacy</h3>
                <p className="text-sm text-muted-foreground">Protect sensitive information</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Face Blur</Label>
                  <p className="text-sm text-muted-foreground">
                    Blur faces in saved media
                  </p>
                </div>
                <Switch checked={faceBlur} onCheckedChange={setFaceBlur} />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Data Retention</Label>
                <Select defaultValue="30">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">7 days</SelectItem>
                    <SelectItem value="30">30 days</SelectItem>
                    <SelectItem value="90">90 days</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>

          {/* Notifications */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Bell className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <h3>Notifications</h3>
                <p className="text-sm text-muted-foreground">Alert preferences</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Activity Alerts</Label>
                  <p className="text-sm text-muted-foreground">
                    Notify when events detected
                  </p>
                </div>
                <Switch
                  checked={notifications}
                  onCheckedChange={setNotifications}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Email</Label>
                <Input type="email" placeholder="your@email.com" />
              </div>
            </div>
          </Card>

          <div className="flex justify-end">
            <Button onClick={handleSave}>Save Changes</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
