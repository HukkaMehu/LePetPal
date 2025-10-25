#!/usr/bin/env python3
"""
LePetPal Backend Startup Script

This script initializes hardware adapters and starts the Flask REST API server.
It loads configuration from environment variables and provides graceful shutdown.
"""

import os
import sys
import signal
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


def setup_logging():
    """Configure JSON-formatted logging with timestamp, level, and request_id fields."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'lepetpal.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def load_configuration():
    """Load and validate configuration from environment variables."""
    config = {
        # Server configuration
        'PORT': int(os.getenv('PORT', 5000)),
        'HOST': os.getenv('HOST', '0.0.0.0'),
        
        # Camera configuration
        'CAMERA_INDEX': int(os.getenv('CAMERA_INDEX', 0)),
        'STREAM_WIDTH': int(os.getenv('STREAM_WIDTH', 1280)),
        'STREAM_HEIGHT': int(os.getenv('STREAM_HEIGHT', 720)),
        'STREAM_FPS': int(os.getenv('STREAM_FPS', 15)),
        
        # Detection thresholds
        'CONFIDENCE_THRESHOLD': float(os.getenv('CONFIDENCE_THRESHOLD', 0.7)),
        'DETECTION_TIMEOUT_MS': int(os.getenv('DETECTION_TIMEOUT_MS', 10000)),
        
        # Hardware configuration
        'USE_MOCK_HARDWARE': os.getenv('USE_MOCK_HARDWARE', 'true').lower() == 'true',
        'SERVO_PIN': int(os.getenv('SERVO_PIN', 18)),
        'SERVO_DISPENSE_DURATION_MS': int(os.getenv('SERVO_DISPENSE_DURATION_MS', 1000)),
        
        # Safety configuration
        'JOINT_LIMIT_MARGIN': float(os.getenv('JOINT_LIMIT_MARGIN', 0.1)),
        'GO_HOME_TIMEOUT_MS': int(os.getenv('GO_HOME_TIMEOUT_MS', 1000)),
        
        # Optional authentication
        'API_TOKEN': os.getenv('API_TOKEN'),
        'CORS_ORIGINS': os.getenv('CORS_ORIGINS', '*'),
    }
    
    return config


def initialize_hardware(config, logger):
    """Initialize hardware adapters based on configuration."""
    logger.info(f"Initializing hardware (mock mode: {config['USE_MOCK_HARDWARE']})")
    
    # Import hardware adapters (these would be implemented in other tasks)
    # For now, this is a placeholder structure
    hardware = {
        'camera': None,
        'arm': None,
        'servo': None,
        'tts': None
    }
    
    try:
        if config['USE_MOCK_HARDWARE']:
            logger.info("Using mock hardware adapters for development")
            # Mock adapters would be imported here
            # from adapters.mock import MockCamera, MockLerobotArm, MockServoController, MockTTS
        else:
            logger.info("Using real hardware adapters")
            # Real adapters would be imported here
            # from adapters.hardware import Camera, LerobotArm, ServoController, TTS
        
        logger.info("Hardware initialization complete")
        return hardware
        
    except Exception as e:
        logger.error(f"Hardware initialization failed: {e}")
        raise


def create_app(config, hardware, logger):
    """Create and configure Flask application."""
    # Import Flask app factory (would be implemented in other tasks)
    # from app import create_flask_app
    # app = create_flask_app(config, hardware)
    
    logger.info("Flask application created")
    # return app
    return None  # Placeholder until Flask app is implemented


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point for the backend server."""
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("LePetPal Backend Server Starting")
    logger.info("=" * 60)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        config = load_configuration()
        logger.info(f"Configuration loaded: PORT={config['PORT']}, "
                   f"CAMERA_INDEX={config['CAMERA_INDEX']}, "
                   f"MOCK_HARDWARE={config['USE_MOCK_HARDWARE']}")
        
        # Initialize hardware
        hardware = initialize_hardware(config, logger)
        
        # Create Flask app
        app = create_app(config, hardware, logger)
        
        # Start server
        logger.info(f"Starting Flask server on {config['HOST']}:{config['PORT']}")
        logger.info(f"Health check: http://{config['HOST']}:{config['PORT']}/health")
        logger.info(f"Video feed: http://{config['HOST']}:{config['PORT']}/video_feed")
        
        # Note: Actual Flask app.run() would be called here once implemented
        # app.run(host=config['HOST'], port=config['PORT'], threaded=True)
        
        logger.warning("Flask app not yet implemented - startup script ready for integration")
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
