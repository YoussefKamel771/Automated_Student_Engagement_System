import requests
import pandas as pd
from typing import Optional, List
import time
from core.data_models import SessionData
from config.logging_config import setup_logging
import streamlit as st

logger = setup_logging()

def post_engagement_data(session: SessionData, engaged_status: List[int], 
                        total_time: float, fps: float) -> Optional[dict]:
    """Post engagement data to server with retry logic"""
    summary = {
        "name": session.name,
        "matric_id": session.matric_id,
        "course": session.course,
        "module": session.module,
        "group": session.group,
        "engaged_percentage": (sum(engaged_status) / len(engaged_status) * 100) if engaged_status else 0,
        "total_frames": len(engaged_status),
        "disengaged_seconds": sum(1 for x in engaged_status if x == 0) / fps if engaged_status else 0,
        "time": total_time,
        "fps": fps
    }
    
    # Try to post to server
    for attempt in range(3):
        try:
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/engagement/upload',
                json=summary,
                timeout=10
            )
            response.raise_for_status()
            st.success("Data sent to server successfully.", icon="✅")
            logger.info(f"Server response: {response.json()}")
            return summary
        except requests.exceptions.RequestException as e:
            logger.warning(f"Server attempt {attempt + 1} failed: {e}")
            if attempt == 2:  # Last attempt
                st.error(f"Server error: {e}. Data logged locally.", icon="❌")
                # Save locally as backup
                try:
                    df = pd.DataFrame([summary])
                    df.to_csv("engagement_data.csv", mode='a', header=False, index=False)
                except Exception as save_error:
                    logger.error(f"Failed to save locally: {save_error}")
            time.sleep(1)  # Brief delay between retries
    
    return summary
