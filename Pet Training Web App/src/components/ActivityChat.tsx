import { useState, useEffect, useRef } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { MessageCircle, Send, Loader2, Activity, AlertCircle, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ActivityLogEntry {
  timestamp: string;
  description: string;
}

export default function ActivityChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([]);
  const [status, setStatus] = useState<any>(null);
  const [sidebarWidth, setSidebarWidth] = useState(25); // percentage
  const [isResizing, setIsResizing] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Load activity log and status on mount
  useEffect(() => {
    loadActivityLog();
    loadStatus();
    
    // Refresh activity log every 30 seconds
    const interval = setInterval(() => {
      loadActivityLog();
      loadStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadActivityLog = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/activity-chat/log?limit=20');
      if (response.ok) {
        const data = await response.json();
        setActivityLog(data);
      }
    } catch (error) {
      console.error('Error loading activity log:', error);
    }
  };

  const loadStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/activity-chat/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error loading status:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/activity-chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: input,
          include_activity_log: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message', {
        description: error instanceof Error ? error.message : 'Network error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearActivityLog = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/activity-chat/clear', {
        method: 'POST'
      });
      
      if (response.ok) {
        setActivityLog([]);
        toast.success('Activity log cleared');
        loadStatus();
      } else {
        throw new Error('Failed to clear log');
      }
    } catch (error) {
      console.error('Error clearing activity log:', error);
      toast.error('Failed to clear activity log');
    }
  };

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain between 15% and 50%
      if (newWidth >= 15 && newWidth <= 50) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  return (
    <div ref={containerRef} className="h-full flex relative">
      {/* Activity Log Panel - Resizable */}
      <Card 
        className="flex flex-col flex-shrink-0 overflow-hidden"
        style={{ width: `${sidebarWidth}%` }}
      >
        <div className="p-3 border-b border-border flex-shrink-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              <h3 className="font-semibold text-sm">Activity Log</h3>
            </div>
            {status && (
              <Badge variant={status.openai_available ? "default" : "destructive"} className="text-xs">
                {status.entries_count}
              </Badge>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={clearActivityLog}
            className="w-full"
          >
            <Trash2 className="w-3 h-3 mr-1.5" />
            Clear Log
          </Button>
        </div>

        <ScrollArea className="flex-1 overflow-y-auto">
          <div className="p-3">
            {activityLog.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground py-8">
                <AlertCircle className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-xs">No activity logged</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activityLog.map((entry, index) => (
                  <div key={index} className="text-xs">
                    <div className="text-[10px] text-muted-foreground mb-1 font-mono">
                      {entry.timestamp}
                    </div>
                    <div className="text-foreground leading-relaxed break-words overflow-wrap-anywhere">
                      {entry.description}
                    </div>
                    {index < activityLog.length - 1 && (
                      <Separator className="mt-3" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>

        {status && !status.openai_available && (
          <div className="p-1.5 border-t border-border bg-destructive/10">
            <div className="flex items-center gap-1 text-[10px] text-destructive">
              <AlertCircle className="w-2.5 h-2.5 flex-shrink-0" />
              <div className="font-medium">No API key</div>
            </div>
          </div>
        )}
      </Card>

      {/* Resize Handle */}
      <div
        className={`w-1 hover:w-2 bg-border hover:bg-primary transition-all cursor-col-resize flex-shrink-0 ${
          isResizing ? 'bg-primary w-2' : ''
        }`}
        onMouseDown={handleMouseDown}
        style={{ userSelect: 'none' }}
      />

      {/* Chat Panel */}
      <Card className="flex-1 flex flex-col ml-3">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-primary" />
            <h3 className="font-semibold">Ask About Your Stream</h3>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Ask questions about what's happening in your video stream
          </p>
        </div>

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-4" ref={scrollRef}>
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center text-muted-foreground">
                  <MessageCircle className="w-12 h-12 mb-4 opacity-50" />
                  <p className="text-sm">Start a conversation</p>
                  <p className="text-xs mt-2">
                    Ask questions like "What's my dog doing?" or "Has anyone been in the room?"
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[33%] min-w-[200px] rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <div className="text-sm whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                        <div
                          className={`text-xs mt-1 ${
                            message.role === 'user'
                              ? 'text-primary-foreground/70'
                              : 'text-muted-foreground'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-muted rounded-lg p-3">
                        <Loader2 className="w-4 h-4 animate-spin" />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        <div className="p-4 border-t border-border bg-background">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your stream..."
              disabled={loading || !status?.openai_available}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || loading || !status?.openai_available}
              size="icon"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
