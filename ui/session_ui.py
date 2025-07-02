import streamlit as st
import cv2
import dlib
import time
import numpy as np
import pandas as pd
from imutils import face_utils
import imutils
from core.engagement_detector import EngagementDetector
from core.camera_manager import CameraManager
from services.tts_service import get_tts_manager
from services.api_service import post_engagement_data
from utils.context_managers import video_stream_context
from config.settings import EngagementConfig
from config.logging_config import setup_logging

logger = setup_logging()

def run_engagement_session(session, model_path: str):
    """Main engagement monitoring session"""
    try:
        fps, camera_index = CameraManager.get_best_camera()
    except RuntimeError as e:
        st.error(f"Camera error: {e}", icon="❌")
        return
    
    # Initialize components
    config = EngagementConfig()
    detector_engine = EngagementDetector(config, fps)

    # Get TTS manager instance
    tts = get_tts_manager()
    
    # Load dlib models
    try:
        face_detector = dlib.get_frontal_face_detector()
        landmark_predictor = dlib.shape_predictor(model_path)
    except Exception as e:
        st.error(f"Error loading face detection models: {e}", icon="❌")
        logger.error(f"Model loading error: {e}")
        return
    
    # UI placeholders
    stframe = st.empty()
    timer_placeholder = st.empty()
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    start_time = None
    last_alert_time = 0
    last_disengaged_status = False
    
    with video_stream_context(camera_index) as vs:
        while True:
            # Frame capture with retry logic
            frame = None
            for attempt in range(3):
                frame = vs.read()
                if frame is not None:
                    break
                time.sleep(0.1)
            
            if frame is None:
                st.error("Failed to capture frame", icon="❌")
                break
            
            # Process frame
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray, 0)
            
            current_time = int(time.time())
            
            # Update timer and progress
            if start_time:
                elapsed = current_time - start_time
                remaining = session.duration * 60 - elapsed
                progress = min(elapsed / (session.duration * 60), 1.0)
                
                if remaining >= 0:
                    mins, secs = divmod(remaining, 60)
                    timer_placeholder.markdown(f"**Time Remaining**: {mins:02d}:{secs:02d}")
                    progress_placeholder.progress(progress)
                else:
                    break  # Session ended
            
            # Process faces for engagement detection
            ear = 0
            if len(faces) > 0:
                # Use the largest face
                face = max(faces, key=lambda rect: rect.width() * rect.height())
                landmarks = landmark_predictor(gray, face)
                landmarks = face_utils.shape_to_np(landmarks)
                
                # Extract eye regions
                left_eye = landmarks[detector_engine.left_eye_start:detector_engine.left_eye_end]
                right_eye = landmarks[detector_engine.right_eye_start:detector_engine.right_eye_end]
                
                # Calculate EAR
                left_ear = detector_engine.eye_aspect_ratio(left_eye)
                right_ear = detector_engine.eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0
                ear = detector_engine.smooth_ear(ear)
                
                # Draw eye contours
                left_hull = cv2.convexHull(left_eye)
                right_hull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
            
            # Calibration phase
            if not detector_engine.is_calibrated:
                calibration_progress = len(detector_engine.calibration_ears) / (config.CALIBRATION_DURATION * fps)
                status_placeholder.markdown(f"**Calibrating...** {calibration_progress:.1%}")
                cv2.putText(frame, "Calibrating... Look at screen", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                if not detector_engine.calibrate(ear):
                    continue  # Keep calibrating
                else:
                    start_time = current_time
                    st.info(f"Calibration complete! Threshold: {detector_engine.ear_thresh:.3f}", icon="✅")
            else:
                # Engagement detection
                disengaged, status = detector_engine.detect_engagement(ear, current_time)
                
                # Dynamic threshold adjustment
                detector_engine.update_threshold_dynamically(current_time, start_time)
                
                # Alert management
                logger.info(f"Processing frame at time {current_time}, disengaged: {disengaged}, ear: {ear:.3f}")
                # Alert management (improved version)
                if disengaged and (current_time - last_alert_time) >= config.ALERT_COOLDOWN:
                    # Only speak if we weren't disengaged in the previous frame
                    # This prevents continuous alerts for sustained disengagement
                    if not last_disengaged_status:
                        alert_message = "Please stay engaged!"
                        tts.speak(alert_message)
                        logger.info(f"Alert triggered: {alert_message}")
                        last_alert_time = current_time
                    elif (current_time - last_alert_time) >= (config.ALERT_COOLDOWN * 2):
                        # Send reminder after double the cooldown period for sustained disengagement
                        reminder_message = "Please focus on the screen!"
                        tts.speak(reminder_message)
                        logger.info(f"Reminder triggered: {reminder_message}")
                        last_alert_time = current_time

                last_disengaged_status = disengaged
                
                # Update UI
                status_color_text = 'red' if disengaged else 'green'
                status_placeholder.markdown(
                    f"**Status**: <span style='color: {status_color_text}'>{status}</span>", 
                    unsafe_allow_html=True
                )
                
                # Frame annotations
                status_color_cv = (0, 0, 255) if disengaged else (0, 255, 0)
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color_cv, 2)
                cv2.putText(frame, f"EAR: {ear:.3f}", (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame, f"Disengaged: {detector_engine.total_disengaged/fps:.1f}s", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # Display frame
            stframe.image(frame, channels="BGR")
            
            # Check for session end
            if start_time and current_time - start_time >= session.duration * 60:
                break
    
    # Session completed
    if detector_engine.engaged_status:
        timer_placeholder.markdown("**Session Completed!**")
        progress_placeholder.progress(1.0)
        
        # Post data and show summary
        summary = post_engagement_data(session, detector_engine.engaged_status, 
                                     session.duration * 60, fps)
        
        st.success(f"Session ended. Total disengaged: {detector_engine.total_disengaged/fps:.1f}s", icon="✅")
        
        # Create engagement chart
        st.subheader("📊 Engagement Summary")
        
        if summary:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Engagement", f"{summary['engaged_percentage']:.1f}%")
            with col2:
                st.metric("Disengaged Time", f"{summary['disengaged_seconds']:.1f}s")
            with col3:
                st.metric("Total Frames", summary['total_frames'])
        
        # Engagement timeline
        if len(detector_engine.engaged_status) > 0:
            df = pd.DataFrame({
                "Time (s)": [i/fps for i in range(len(detector_engine.engaged_status))],
                "Engagement": detector_engine.engaged_status
            })
            st.line_chart(df.set_index("Time (s)"), height=300)