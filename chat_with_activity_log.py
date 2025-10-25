"""
Chat with Activity Log
Ask questions about what happened in your video stream.

Usage:
    pip install openai python-dotenv
    # Edit .env.logger with your API key
    python chat_with_activity_log.py
"""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.logger
load_dotenv('.env.logger')

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ActivityLogChat:
    def __init__(self, log_file, provider="openai", model=None):
        self.log_file = Path(log_file)
        self.provider = provider.lower()
        
        if not self.log_file.exists():
            print(f"⚠️  Log file not found: {log_file}")
            print(f"⚠️  The logger will create it once it captures the first frame.")
            print(f"⚠️  Creating empty log file for now...")
            self.log_file.touch()
            self.activity_log = ""
        else:
            # Load activity log
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.activity_log = f.read()
            
            if self.activity_log.strip():
                print(f"✅ Loaded {len(self.activity_log.splitlines())} activity entries")
            else:
                print(f"⚠️  Log file is empty. Waiting for logger to capture frames...")
        
        # Initialize API client
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"
            
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
    
    def ask_openai(self, question):
        """Ask question using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant analyzing video stream activity logs. Here's the activity log:\n\n{self.activity_log}\n\nAnswer questions about what happened in the stream based on this log."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    
    def ask_gemini(self, question):
        """Ask question using Gemini."""
        prompt = f"""You are analyzing video stream activity logs. Here's the activity log:

{self.activity_log}

Question: {question}

Answer based on the activity log above."""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def ask(self, question):
        """Ask a question about the activity log."""
        # Reload log file to get latest entries
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.activity_log = f.read()
        
        if not self.activity_log.strip():
            return "The activity log is still empty. The logger hasn't captured any frames yet. Please wait a moment for the first capture."
        
        if self.provider == "openai":
            return self.ask_openai(question)
        else:
            return self.ask_gemini(question)
    
    def chat(self):
        """Interactive chat loop."""
        print("\n💬 Chat with your activity log (type 'quit' to exit)\n")
        
        while True:
            try:
                question = input("You: ").strip()
                if not question:
                    continue
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                
                print("\n🤖 AI: ", end="", flush=True)
                answer = self.ask(question)
                print(answer + "\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
        
        print("\n👋 Goodbye!")


def main():
    parser = argparse.ArgumentParser(description="Chat with activity log")
    parser.add_argument("--log",
                       help="Activity log file")
    parser.add_argument("--provider", choices=["openai", "gemini"],
                       help="AI provider")
    parser.add_argument("--model", help="Model name (optional)")
    parser.add_argument("--question", help="Single question (non-interactive)")
    
    args = parser.parse_args()
    
    # Use env vars as defaults, command line args override
    log_file = args.log or os.getenv("LOG_FILE", "stream_activity.txt")
    provider = args.provider or os.getenv("AI_PROVIDER", "openai")
    model = args.model or os.getenv("AI_MODEL")
    
    chat = ActivityLogChat(
        log_file=log_file,
        provider=provider,
        model=model
    )
    
    if args.question:
        # Single question mode
        answer = chat.ask(args.question)
        print(answer)
    else:
        # Interactive chat mode
        chat.chat()


if __name__ == "__main__":
    main()
