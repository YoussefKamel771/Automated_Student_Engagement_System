import numpy as np
from collections import deque
from imutils import face_utils
from config.settings import EngagementConfig
from typing import Tuple

class EngagementDetector:
    """Optimized engagement detection class"""
    
    def __init__(self, config: EngagementConfig, fps: float):
        self.config = config
        self.fps = fps
        self.ear_thresh = config.INITIAL_EAR_THRESH
        self.ear_buffer = deque(maxlen=config.EAR_SMOOTHING_WINDOW)
        self.ear_history = deque(maxlen=int(fps * 60))  # Keep 1 minute of history
        self.counter = 0
        self.total_disengaged = 0
        self.calibration_ears = []
        self.last_alert_time = 0
        self.blink_counter = 0
        self.lookdown_counter = 0
        self.engaged_status = []
        self.is_calibrated = False
        
        # Eye landmark indices
        (self.left_eye_start, self.left_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.right_eye_start, self.right_eye_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    
    @staticmethod
    def eye_aspect_ratio(eye_points: np.ndarray) -> float:
        """Calculate Eye Aspect Ratio efficiently"""
        # Vectorized calculation
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        return (A + B) / (2.0 * C) if C > 0 else 0
    
    def smooth_ear(self, ear: float) -> float:
        """Apply smoothing to EAR values"""
        self.ear_buffer.append(ear)
        return np.mean(self.ear_buffer)
    
    def is_blink(self, ear: float) -> bool:
        """Detect if current EAR indicates a blink"""
        if len(self.ear_history) < int(self.config.BLINK_DURATION * self.fps):
            return False
        
        # Simplified blink detection - just check for rapid drop
        if len(self.ear_buffer) >= 2:
            prev_ear = list(self.ear_buffer)[-2] if len(self.ear_buffer) > 1 else ear
            return (ear < self.ear_thresh * 0.7 and prev_ear > self.ear_thresh * 0.9)
        return False
    
    def calibrate(self, ear: float) -> bool:
        """Calibrate EAR threshold"""
        # Only add valid EAR values (not zero, not extremely low)
        if ear > 0.1:  # Simple threshold instead of complex blink detection during calibration
            self.calibration_ears.append(ear)
        
        required_frames = int(self.config.CALIBRATION_DURATION * self.fps)
        
        # Check if we have enough frames for calibration
        if len(self.calibration_ears) >= required_frames:
            mean_ear = np.mean(self.calibration_ears)
            self.ear_thresh = np.clip(mean_ear * 0.85, 
                                    self.config.MIN_EAR_THRESH, 
                                    self.config.MAX_EAR_THRESH)
            self.is_calibrated = True
            return True
        return False
    
    def update_threshold_dynamically(self, current_time: int, start_time: int):
        """Update EAR threshold based on recent data"""
        if ((current_time - start_time) % self.config.DYNAMIC_ADJUSTMENT_INTERVAL == 0 and 
            len(self.ear_history) > self.fps * self.config.DYNAMIC_ADJUSTMENT_INTERVAL):
            
            recent_ears = [e for e in list(self.ear_history)[-int(self.fps * self.config.DYNAMIC_ADJUSTMENT_INTERVAL):] 
                          if e > self.ear_thresh * 0.9]
            
            if recent_ears:
                new_thresh = np.clip(np.mean(recent_ears) * 0.85,
                                   self.config.MIN_EAR_THRESH,
                                   self.config.MAX_EAR_THRESH)
                if abs(new_thresh - self.ear_thresh) > 0.01:  # Only update if significant change
                    self.ear_thresh = new_thresh
    
    def detect_engagement(self, ear: float, current_time: float) -> Tuple[bool, str]:
        """Main engagement detection logic"""
        self.ear_history.append(ear)
        
        # Handle face not detected (ear = 0)
        if ear == 0:
            self.lookdown_counter += 1
            disengaged = self.lookdown_counter >= int(self.config.DISENGAGED_THRESHOLD * self.fps)
        else:
            self.lookdown_counter = 0
            
            # Check for blink vs sustained eye closure
            if self.is_blink(ear):
                self.blink_counter += 1
                if self.blink_counter <= int(self.config.BLINK_DURATION * self.fps):
                    disengaged = False  # Ignore blinks
                else:
                    disengaged = True
            else:
                self.blink_counter = 0
                
                # Check sustained eye closure
                if ear < self.ear_thresh:
                    self.counter += 1
                else:
                    self.counter = 0
                
                disengaged = self.counter >= int(self.config.DISENGAGED_THRESHOLD * self.fps)
        
        if disengaged:
            self.total_disengaged += 1
        
        self.engaged_status.append(0 if disengaged else 1)
        
        # Determine status text
        if ear == 0:
            status = "Looking Away" if disengaged else "Engaged"
        else:
            status = "Eyes Closed" if disengaged else "Engaged"
        
        return disengaged, status