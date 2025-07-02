import pyttsx3
import threading
import queue
import atexit
import time
from config.logging_config import setup_logging

logger = setup_logging()

class TTSManager:
    """Thread-safe TTS manager with improved reliability"""
    
    def __init__(self):
        self.engine = None
        self.tts_queue = queue.Queue(maxsize=10)  # Limit queue size
        self.worker_thread = None
        self.is_running = True
        self._initialize_engine()
        self._start_worker()
    
    def _initialize_engine(self):
        """Initialize TTS engine with error handling"""
        try:
            self.engine = pyttsx3.init()
            # Set properties for better reliability
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            
            # Get available voices (optional - helps with some systems)
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.warning(f"TTS initialization failed: {e}")
            self.engine = None
    
    def _start_worker(self):
        """Start background worker for TTS"""
        if self.engine:
            self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.worker_thread.start()
            logger.info("TTS worker thread started")
    
    def _tts_worker(self):
        """Background worker for TTS processing with improved error handling"""
        while self.is_running:
            try:
                # Use timeout to allow thread to check is_running periodically
                message = self.tts_queue.get(timeout=1)
                if message is None:  # Shutdown signal
                    break
                    
                if self.engine:
                    try:
                        # Clear any pending speech before speaking new message
                        self.engine.stop()
                        
                        # Speak the message
                        self.engine.say(message)
                        self.engine.runAndWait()
                        
                        logger.info(f"TTS spoke: {message}")
                        
                    except Exception as speak_error:
                        logger.error(f"TTS speaking error: {speak_error}")
                        # Try to reinitialize engine if speaking fails
                        self._reinitialize_engine()
                        
            except queue.Empty:
                continue  # Normal timeout, continue loop
            except Exception as e:
                logger.error(f"TTS worker error: {e}")
                # Small delay before continuing to prevent rapid error loops
                time.sleep(0.1)
    
    def _reinitialize_engine(self):
        """Reinitialize TTS engine if it becomes unresponsive"""
        try:
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                
            # Create new engine instance
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            
            logger.info("TTS engine reinitialized")
            
        except Exception as e:
            logger.error(f"TTS reinitialization failed: {e}")
            self.engine = None
    
    def speak(self, message: str):
        """Add message to TTS queue with improved error handling"""
        if not self.engine:
            logger.warning("TTS engine not available")
            return
            
        try:
            # Clear queue if it's getting full to prevent old messages from piling up
            if self.tts_queue.qsize() > 5:
                logger.warning("TTS queue full, clearing old messages")
                while not self.tts_queue.empty():
                    try:
                        self.tts_queue.get_nowait()
                    except queue.Empty:
                        break
            
            # Add new message
            self.tts_queue.put_nowait(message)
            logger.info(f"TTS message queued: {message}")
            
        except queue.Full:
            logger.warning("TTS queue full, skipping message")
        except Exception as e:
            logger.error(f"Error queuing TTS message: {e}")
    
    def stop(self):
        """Stop the TTS manager"""
        self.is_running = False
        if self.tts_queue:
            self.tts_queue.put(None)  # Signal worker to stop
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        logger.info("TTS manager stopped")

# Global instance
tts_manager = None

def get_tts_manager():
    """Get or create TTS manager instance"""
    global tts_manager
    if tts_manager is None:
        tts_manager = TTSManager()
    return tts_manager

# Register cleanup function
atexit.register(lambda: tts_manager.stop() if tts_manager else None)
