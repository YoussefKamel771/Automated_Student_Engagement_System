from dataclasses import dataclass

@dataclass
class EngagementConfig:
    """Configuration class for engagement detection parameters"""
    INITIAL_EAR_THRESH: float = 1.0
    MIN_EAR_THRESH: float = 0.15
    MAX_EAR_THRESH: float = 0.35
    CALIBRATION_DURATION: int = 7  # seconds
    BLINK_DURATION: float = 0.3  # seconds
    EAR_SMOOTHING_WINDOW: int = 5
    ALERT_COOLDOWN: int = 5  # seconds
    DISENGAGED_THRESHOLD: float = 1.5  # seconds
    DYNAMIC_ADJUSTMENT_INTERVAL: int = 30  # seconds
    