from imutils.video import VideoStream
import time
from contextlib import contextmanager
import cv2

@contextmanager
def video_stream_context(camera_index: int):
    """Context manager for video stream"""
    vs = VideoStream(src=camera_index, apiPreference=cv2.CAP_DSHOW).start()
    time.sleep(1.0)
    try:
        yield vs
    finally:
        vs.stop()