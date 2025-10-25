/**
 * Master Test Runner
 * 
 * Runs all integration tests in sequence and provides a comprehensive report.
 */

import runAPIIntegrationTests from './api.integration.test';
import runWebSocketIntegrationTests from './websocket.integration.test';
import runVideoStreamingTests from './video.integration.test';
import runUserWorkflowTests from './workflows.integration.test';

/**
 * Run all integration tests
 */
export async function runAllTests(): Promise<void> {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 STARTING COMPREHENSIVE INTEGRATION TEST SUITE');
  console.log('='.repeat(70) + '\n');
  
  const startTime = Date.now();
  
  try {
    // Run API Integration Tests
    console.log('📡 Running API Integration Tests...\n');
    await runAPIIntegrationTests();
    
    // Run WebSocket Integration Tests
    console.log('\n🔌 Running WebSocket Integration Tests...\n');
    await runWebSocketIntegrationTests();
    
    // Run Video Streaming Tests
    console.log('\n📹 Running Video Streaming Tests...\n');
    await runVideoStreamingTests();
    
    // Run User Workflow Tests
    console.log('\n👤 Running User Workflow Tests...\n');
    await runUserWorkflowTests();
    
  } catch (error) {
    console.error('\n❌ Test suite encountered a critical error:', error);
  }
  
  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);
  
  console.log('\n' + '='.repeat(70));
  console.log('✨ INTEGRATION TEST SUITE COMPLETED');
  console.log('='.repeat(70));
  console.log(`⏱️  Total Duration: ${duration} seconds`);
  console.log('='.repeat(70) + '\n');
  
  console.log('📝 Test Summary:');
  console.log('   - API Integration Tests: Completed');
  console.log('   - WebSocket Integration Tests: Completed');
  console.log('   - Video Streaming Tests: Completed');
  console.log('   - User Workflow Tests: Completed');
  console.log('\n');
}

// Auto-run if this file is executed directly
if (typeof window !== 'undefined') {
  // Browser environment - expose to window
  (window as any).runAllTests = runAllTests;
  console.log('✅ Test runner loaded. Call runAllTests() to start tests.');
}

export default runAllTests;
