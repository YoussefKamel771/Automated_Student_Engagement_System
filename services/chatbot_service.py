import subprocess
import os
import atexit
import time
from config.logging_config import setup_logging

logger = setup_logging()

class ChatbotManager:
    """Manage chatbot subprocess"""
    
    def __init__(self, port: int = 8502):
        self.port = port
        self.process = None
        atexit.register(self.stop)
    
    def start(self):
        """Start chatbot subprocess"""
        if not self.process and os.path.exists("pages/chatbot.py"):
            try:
                self.process = subprocess.Popen(
                    ["streamlit", "run", "pages/chatbot.py", "--server.port", str(self.port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                logger.info(f"Started chatbot on port {self.port}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to start chatbot: {e}")
    
    def stop(self):
        """Stop chatbot subprocess"""
        if self.process:
            self.process.terminate()
            self.process = None
            logger.info("Chatbot subprocess terminated")