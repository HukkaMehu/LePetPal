/**
 * Test Page Component
 * 
 * Provides a UI for running integration tests and viewing results.
 */

import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Loader2, PlayCircle, CheckCircle2, XCircle } from 'lucide-react';
import runAPIIntegrationTests from '../tests/api.integration.test';
import runWebSocketIntegrationTests from '../tests/websocket.integration.test';
import runVideoStreamingTests from '../tests/video.integration.test';
import runUserWorkflowTests from '../tests/workflows.integration.test';
import runAllTests from '../tests/runAllTests';

interface TestResult {
  name: string;
  status: 'idle' | 'running' | 'passed' | 'failed';
  output: string[];
}

export default function TestPage() {
  const [testResults, setTestResults] = useState<TestResult[]>([
    { name: 'API Integration Tests', status: 'idle', output: [] },
    { name: 'WebSocket Integration Tests', status: 'idle', output: [] },
    { name: 'Video Streaming Tests', status: 'idle', output: [] },
    { name: 'User Workflow Tests', status: 'idle', output: [] },
  ]);
  const [isRunningAll, setIsRunningAll] = useState(false);
  const [consoleOutput, setConsoleOutput] = useState<string[]>([]);

  // Capture console output
  const captureConsole = (callback: () => void) => {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const output: string[] = [];

    console.log = (...args: any[]) => {
      output.push(args.join(' '));
      originalLog(...args);
    };

    console.error = (...args: any[]) => {
      output.push(`ERROR: ${args.join(' ')}`);
      originalError(...args);
    };

    console.warn = (...args: any[]) => {
      output.push(`WARN: ${args.join(' ')}`);
      originalWarn(...args);
    };

    callback();

    console.log = originalLog;
    console.error = originalError;
    console.warn = originalWarn;

    return output;
  };

  const runTest = async (index: number, testFn: () => Promise<void>) => {
    setTestResults(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], status: 'running', output: [] };
      return updated;
    });

    try {
      const output = captureConsole(() => {
        testFn().then(() => {
          setTestResults(prev => {
            const updated = [...prev];
            updated[index] = { ...updated[index], status: 'passed' };
            return updated;
          });
        }).catch(() => {
          setTestResults(prev => {
            const updated = [...prev];
            updated[index] = { ...updated[index], status: 'failed' };
            return updated;
          });
        });
      });

      setTestResults(prev => {
        const updated = [...prev];
        updated[index] = { ...updated[index], output };
        return updated;
      });
    } catch (error) {
      setTestResults(prev => {
        const updated = [...prev];
        updated[index] = { ...updated[index], status: 'failed', output: [String(error)] };
        return updated;
      });
    }
  };

  const runAllTestsHandler = async () => {
    setIsRunningAll(true);
    setConsoleOutput([]);

    const originalLog = console.log;
    const originalError = console.error;
    const output: string[] = [];

    console.log = (...args: any[]) => {
      const message = args.join(' ');
      output.push(message);
      setConsoleOutput(prev => [...prev, message]);
      originalLog(...args);
    };

    console.error = (...args: any[]) => {
      const message = `ERROR: ${args.join(' ')}`;
      output.push(message);
      setConsoleOutput(prev => [...prev, message]);
      originalError(...args);
    };

    try {
      await runAllTests();
    } catch (error) {
      console.error('Test suite error:', error);
    }

    console.log = originalLog;
    console.error = originalError;
    setIsRunningAll(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      case 'passed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <PlayCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Integration Tests</h1>
          <p className="text-muted-foreground mt-2">
            Run comprehensive integration tests to verify all functionality
          </p>
        </div>
        <Button
          onClick={runAllTestsHandler}
          disabled={isRunningAll}
          size="lg"
        >
          {isRunningAll ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Running Tests...
            </>
          ) : (
            <>
              <PlayCircle className="mr-2 h-4 w-4" />
              Run All Tests
            </>
          )}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {testResults.map((test, index) => (
          <Card key={test.name}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(test.status)}
                  <CardTitle className="text-lg">{test.name}</CardTitle>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const testFunctions = [
                      runAPIIntegrationTests,
                      runWebSocketIntegrationTests,
                      runVideoStreamingTests,
                      runUserWorkflowTests,
                    ];
                    runTest(index, testFunctions[index]);
                  }}
                  disabled={test.status === 'running'}
                >
                  {test.status === 'running' ? 'Running...' : 'Run Test'}
                </Button>
              </div>
              <CardDescription>
                {test.status === 'idle' && 'Ready to run'}
                {test.status === 'running' && 'Test in progress...'}
                {test.status === 'passed' && 'All tests passed'}
                {test.status === 'failed' && 'Some tests failed'}
              </CardDescription>
            </CardHeader>
            {test.output.length > 0 && (
              <CardContent>
                <ScrollArea className="h-32 w-full rounded border p-2">
                  <pre className="text-xs">
                    {test.output.join('\n')}
                  </pre>
                </ScrollArea>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {consoleOutput.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Test Output</CardTitle>
            <CardDescription>Complete test execution log</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96 w-full rounded border p-4">
              <pre className="text-xs font-mono">
                {consoleOutput.join('\n')}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Test Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Prerequisites</h3>
            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
              <li>Backend server must be running on {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}</li>
              <li>AI service should be running on {import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8001'}</li>
              <li>WebSocket server must be accessible at {import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}</li>
              <li>Database should be populated with test data</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">What Gets Tested</h3>
            <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
              <li>API Integration: All REST API endpoints and error handling</li>
              <li>WebSocket: Real-time connections and message handling</li>
              <li>Video Streaming: MJPEG stream and video metrics</li>
              <li>User Workflows: Complete end-to-end user scenarios</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
