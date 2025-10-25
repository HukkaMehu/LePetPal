"""
Stream Activity Logger
Captures frames from video stream and logs activity descriptions using vision AI.

Usage:
    pip install opencv-python openai pillow python-dotenv
    
    # Edit .env.logger with your API key
    python stream_activity_logger.py
"""
import cv2
import base64
import time
import argparse
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env.logger
load_dotenv('.env.logger')

# Try importing API clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Run: pip install openai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not installed. Run: pip install google-generativeai")


class StreamActivityLogger:
    def __init__(self, video_source, log_file="stream_activity.txt", 
                 interval=10, provider="openai", model=None):
        """
        Args:
            video_source: URL or camera index (0 for webcam)
            log_file: Path to activity log file
            interval: Seconds between captures
            provider: "openai" or "gemini"
            model: Model name (optional, uses defaults)
        """
        self.video_source = video_source
        self.log_file = Path(log_file)
        self.interval = interval
        self.provider = provider.lower()
        
        # Initialize API client
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"  # Cheaper vision model
            
        elif self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Gemini not installed")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model or "gemini-1.5-flash")
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Open video stream
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {video_source}")
        
        print(f"✅ Connected to video source")
        print(f"✅ Using {self.provider} ({self.model if self.provider == 'openai' else 'gemini-1.5-flash'})")
        print(f"✅ Logging to: {self.log_file}")
        print(f"✅ Capture interval: {interval}s")
    
    def capture_frame(self):
        """Capture a single frame from the stream."""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def frame_to_base64(self, frame):
        """Convert OpenCV frame to base64 JPEG."""
        # Resize to reduce API costs
        height, width = frame.shape[:2]
        if width > 800:
            scale = 800 / width
            frame = cv2.resize(frame, (800, int(height * scale)))
        
        # Convert to JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode('utf-8')
    
    def describe_frame_openai(self, frame_base64):
        """Get description from OpenAI Vision API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Briefly describe what's happening in this image. Focus on: people, pets, movement, and notable activities. Keep it under 50 words."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame_base64}",
                                    "detail": "low"  # Cheaper
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def describe_frame_gemini(self, frame_base64):
        """Get description from Gemini Vision API."""
        try:
            # Decode base64 to PIL Image
            image_data = base64.b64decode(frame_base64)
            image = Image.open(BytesIO(image_data))
            
            prompt = "Briefly describe what's happening in this image. Focus on: people, pets, movement, and notable activities. Keep it under 50 words."
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def log_activity(self, description):
        """Append activity description to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {description}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(f"📝 {log_entry.strip()}")
    
    def run(self):
        """Main loop: capture frames and log activity."""
        print("\n🎬 Starting activity logging... (Press Ctrl+C to stop)\n")
        
        try:
            while True:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    print("⚠️  Failed to capture frame, retrying...")
                    time.sleep(1)
                    continue
                
                # Convert to base64
                frame_base64 = self.frame_to_base64(frame)
                
                # Get description from AI
                if self.provider == "openai":
                    description = self.describe_frame_openai(frame_base64)
                else:
                    description = self.describe_frame_gemini(frame_base64)
                
                # Log it
                self.log_activity(description)
                
                # Wait for next interval
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Stopped logging")
        finally:
            self.cap.release()
            print(f"📄 Activity log saved to: {self.log_file.absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Log video stream activity using vision AI")
    parser.add_argument("--source", 
                       help="Video source (URL or camera index)")
    parser.add_argument("--log",
                       help="Log file path")
    parser.add_argument("--interval", type=int,
                       help="Seconds between captures")
    parser.add_argument("--provider", choices=["openai", "gemini"],
                       help="AI provider")
    parser.add_argument("--model", help="Model name (optional)")
    
    args = parser.parse_args()
    
    # Use env vars as defaults, command line args override
    source = args.source or os.getenv("VIDEO_SOURCE", "0")
    log_file = args.log or os.getenv("LOG_FILE", "stream_activity.txt")
    interval = args.interval or int(os.getenv("CAPTURE_INTERVAL", "10"))
    provider = args.provider or os.getenv("AI_PROVIDER", "openai")
    model = args.model or os.getenv("AI_MODEL")
    
    # Convert source to int if it's a digit
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    # Create and run logger
    logger = StreamActivityLogger(
        video_source=source,
        log_file=log_file,
        interval=interval,
        provider=provider,
        model=model
    )
    logger.run()


if __name__ == "__main__":
    main()
