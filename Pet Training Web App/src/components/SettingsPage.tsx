import { useState } from 'react';
import { Card } from './ui/card';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Separator } from './ui/separator';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Video, Shield, Bell } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

export default function SettingsPage() {
  const [streamProtocol, setStreamProtocol] = useState('webrtc');
  const [faceBlur, setFaceBlur] = useState(false);
  const [notifications, setNotifications] = useState(true);

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
          {/* Camera & Stream */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Video className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <h3>Camera & Stream</h3>
                <p className="text-sm text-muted-foreground">Video quality and protocol</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Stream Protocol</Label>
                <Select value={streamProtocol} onValueChange={setStreamProtocol}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="webrtc">WebRTC</SelectItem>
                    <SelectItem value="mjpeg">MJPEG</SelectItem>
                    <SelectItem value="hls">HLS</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Quality</Label>
                <Select defaultValue="balanced">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low Latency (720p)</SelectItem>
                    <SelectItem value="balanced">Balanced (1080p)</SelectItem>
                    <SelectItem value="high">High Quality (4K)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
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
