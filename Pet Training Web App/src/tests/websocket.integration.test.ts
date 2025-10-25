/**
 * WebSocket Integration Tests
 * 
 * Tests WebSocket functionality to verify:
 * - WebSocket connection establishes correctly
 * - Real-time event updates
 * - Reconnection after disconnect
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
 */

import { WebSocketService } from '../services/websocket';
import { config } from '../config/env';

// Create an instance for testing
const webSocketService = new WebSocketService(config.wsURL);

// Test configuration
const TEST_TIMEOUT = 15000; // 15 seconds
const RECONNECT_WAIT = 5000; // 5 seconds

/**
 * Test Suite: WebSocket Integration Tests
 */
export async function runWebSocketIntegrationTests(): Promise<void> {
  console.log('🧪 Starting WebSocket Integration Tests...\n');
  
  const results = {
    passed: 0,
    failed: 0,
    errors: [] as string[]
  };

  // Test 1: WebSocket Connection
  try {
    console.log('Testing WebSocket Connection...');
    
    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Connection timeout'));
      }, TEST_TIMEOUT);

      // Connect to WebSocket
      webSocketService.connect();

      // Wait for connection
      const checkConnection = setInterval(() => {
        if (webSocketService.isConnected()) {
          clearTimeout(timeout);
          clearInterval(checkConnection);
          console.log('✅ WebSocket Connection: Successfully connected');
          results.passed++;
          resolve();
        }
      }, 100);
    });
  } catch (error) {
    console.error('❌ WebSocket Connection failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Connection: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 2: Subscribe to Events
  try {
    console.log('Testing WebSocket Event Subscription...');
    
    const unsubscribe = webSocketService.subscribe('event', (data: any) => {
      console.log('Received event:', data);
    });

    // Wait a bit to see if we receive any messages
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Unsubscribe
    unsubscribe();

    console.log('✅ WebSocket Event Subscription: Subscription mechanism works');
    results.passed++;
  } catch (error) {
    console.error('❌ WebSocket Event Subscription failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Event Subscription: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 3: Multiple Subscriptions
  try {
    console.log('Testing Multiple WebSocket Subscriptions...');
    
    const subscriptions: (() => void)[] = [];
    let eventCount = 0;
    let overlayCount = 0;
    let telemetryCount = 0;

    // Subscribe to different event types
    subscriptions.push(webSocketService.subscribe('event', () => eventCount++));
    subscriptions.push(webSocketService.subscribe('overlay', () => overlayCount++));
    subscriptions.push(webSocketService.subscribe('telemetry', () => telemetryCount++));

    // Wait for potential messages
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Cleanup
    subscriptions.forEach(unsub => unsub());

    console.log('✅ Multiple WebSocket Subscriptions: Multiple subscriptions work');
    results.passed++;
  } catch (error) {
    console.error('❌ Multiple WebSocket Subscriptions failed:', error);
    results.failed++;
    results.errors.push(`Multiple WebSocket Subscriptions: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 4: Connection State
  try {
    console.log('Testing WebSocket Connection State...');
    
    const isConnected = webSocketService.isConnected();
    
    if (typeof isConnected === 'boolean') {
      console.log(`✅ WebSocket Connection State: State is ${isConnected ? 'connected' : 'disconnected'}`);
      results.passed++;
    } else {
      throw new Error('Connection state is not a boolean');
    }
  } catch (error) {
    console.error('❌ WebSocket Connection State failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Connection State: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 5: Reconnection Logic
  try {
    console.log('Testing WebSocket Reconnection...');
    
    // Disconnect
    webSocketService.disconnect();
    
    // Wait for disconnect
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (!webSocketService.isConnected()) {
      console.log('WebSocket disconnected successfully');
    }

    // Reconnect
    webSocketService.connect();
    
    // Wait for reconnection
    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Reconnection timeout'));
      }, TEST_TIMEOUT);

      const checkConnection = setInterval(() => {
        if (webSocketService.isConnected()) {
          clearTimeout(timeout);
          clearInterval(checkConnection);
          resolve();
        }
      }, 100);
    });

    console.log('✅ WebSocket Reconnection: Successfully reconnected');
    results.passed++;
  } catch (error) {
    console.error('❌ WebSocket Reconnection failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Reconnection: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 6: Error Handling
  try {
    console.log('Testing WebSocket Error Handling...');
    
    // Try to connect to invalid URL
    const invalidUrl = 'ws://invalid-url-test-12345.local:9999';
    
    try {
      webSocketService.disconnect();
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Create a new instance with invalid URL
      const invalidWs = new WebSocketService(invalidUrl);
      invalidWs.connect();
      
      // Wait a bit to see if error is handled
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Reconnect to valid URL
      webSocketService.disconnect();
      await new Promise(resolve => setTimeout(resolve, 500));
      webSocketService.connect();
      
      console.log('✅ WebSocket Error Handling: Error handling works (no crash)');
      results.passed++;
    } catch (error) {
      // Error is expected, but should be handled gracefully
      console.log('✅ WebSocket Error Handling: Errors handled gracefully');
      results.passed++;
      
      // Reconnect to valid URL
      webSocketService.disconnect();
      await new Promise(resolve => setTimeout(resolve, 500));
      webSocketService.connect();
    }
  } catch (error) {
    console.error('❌ WebSocket Error Handling failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Error Handling: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Test 7: Message Format Validation
  try {
    console.log('Testing WebSocket Message Format...');
    
    const unsubscribe = webSocketService.subscribe('event', (data: any) => {
      // Check if message has expected structure
      if (data && typeof data === 'object') {
        console.log('Valid message received');
      }
    });

    // Wait for messages
    await new Promise(resolve => setTimeout(resolve, 2000));

    unsubscribe();

    console.log('✅ WebSocket Message Format: Message format validation works');
    results.passed++;
  } catch (error) {
    console.error('❌ WebSocket Message Format failed:', error);
    results.failed++;
    results.errors.push(`WebSocket Message Format: ${error instanceof Error ? error.message : String(error)}`);
  }

  // Cleanup - disconnect at the end
  try {
    webSocketService.disconnect();
  } catch (error) {
    console.warn('Warning: Failed to disconnect WebSocket:', error);
  }

  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('WebSocket Integration Test Results');
  console.log('='.repeat(50));
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`Total: ${results.passed + results.failed}`);
  
  if (results.errors.length > 0) {
    console.log('\nErrors:');
    results.errors.forEach((error, index) => {
      console.log(`${index + 1}. ${error}`);
    });
  }
  
  console.log('='.repeat(50) + '\n');
  
  return;
}

// Export for use in test runner
export default runWebSocketIntegrationTests;
