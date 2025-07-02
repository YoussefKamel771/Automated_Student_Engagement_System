import cv2
import time
from config.logging_config import setup_logging

logger = setup_logging()

class CameraManager:
    """Optimized camera management"""
    
    @staticmethod
    def get_best_camera() -> tuple[float, int]:
        """Find the best available camera and calculate its FPS"""
        for index in range(3):
            try:
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    continue
                
                # Set optimal resolution for performance
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                # Calculate actual FPS
                num_frames = 30
                start_time = time.time()
                for _ in range(num_frames):
                    ret, _ = cap.read()
                    if not ret:
                        break
                else:
                    elapsed = time.time() - start_time
                    fps = num_frames / elapsed if elapsed > 0 else 30.0
                    cap.release()
                    logger.info(f"Camera {index} FPS: {fps:.2f}")
                    return fps, index
                
                cap.release()
            except Exception as e:
                logger.error(f"Error testing camera {index}: {e}")
                continue
        
        raise RuntimeError("No suitable camera found")