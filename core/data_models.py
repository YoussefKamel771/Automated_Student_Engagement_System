from dataclasses import dataclass

@dataclass
class SessionData:
    """Data class for session information"""
    name: str
    matric_id: str
    course: str
    group: str
    module: str
    duration: int