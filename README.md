# Automated Student Engagement System (aSES) with Local Chat Assistant

## Overview
The **Automated Student Engagement System (aSES)** is a Streamlit-based application designed to monitor student engagement in real-time using facial landmark detection and eye aspect ratio (EAR) analysis. It tracks whether a student is engaged or disengaged based on eye closure or looking away, providing visual feedback, voice alerts, and engagement summaries. The system is integrated with a **Local Chat Assistant** powered by Google Deepmind's Gemma 3 model (via Ollama), running as a separate page in a distinct process to ensure performance isolation. The chatbot offers contextual assistance, such as answering lecture-related questions or providing engagement tips.

### Features
- **Engagement Monitoring**:
  - Real-time webcam-based face detection using OpenCV and dlib.
  - Calculates EAR to detect disengagement (e.g., eyes closed or looking away).
  - Displays live video feed, engagement status, and session timer in a professional Streamlit UI.
  - Sends engagement data to a server via POST requests or saves locally if the server fails.
  - Visualizes engagement trends with a line chart.
  - Provides voice alerts using text-to-speech (pyttsx3) when disengaged.
- **Local Chat Assistant**:
  - Runs as a separate Streamlit app on a different port, launched as a subprocess.
  - Powered by Gemma 3 (4B) via Ollama for local, privacy-focused AI responses.
  - Supports text input and optional image uploads (logged, not processed).
  - Maintains conversation history in Streamlit session state.
- **Performance Isolation**:
  - Engagement monitoring and chatbot run in separate processes to avoid resource contention.
  - Robust error handling for webcam access, server communication, and model loading.

## Project Structure
```
ases_app/
├── main.py                     # Main Streamlit application
├── config/
│   ├── settings.py            # Configuration classes
│   └── logging_config.py      # Logging setup
├── core/
│   ├── engagement_detector.py # Engagement detection logic
│   ├── camera_manager.py      # Camera handling
│   └── data_models.py         # Data classes
├── services/
│   ├── tts_service.py         # Text-to-speech manager
│   ├── chatbot_service.py     # Chatbot subprocess manager
│   └── api_service.py         # API communication
├── ui/
│   ├── components.py          # UI components and styling
│   └── session_ui.py          # Session UI logic
├── utils/
│   ├── file_utils.py          # File operations
│   └── context_managers.py    # Context managers
├── pages/
│   └── chatbot.py            # Chatbot page
├── requirements.txt
├── shape_predictor_68_face_landmarks.dat
└── README.md
```

## Requirements
- **Python**: 3.8 or higher
- **Dependencies**: Listed in `requirements.txt`
  ```
  streamlit
  opencv-python
  dlib
  imutils
  scipy
  pyttsx3
  requests
  pandas
  ```
- **Hardware**:
  - Webcam (compatible with OpenCV's DirectShow backend).
  - 8GB+ RAM and multi-core CPU (recommended for dlib and Ollama).
- **External Model**:
  - dlib's `shape_predictor_68_face_landmarks.dat` (download from [http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)).
  - Ollama with `gemma3:4b` model installed.
- **Optional**: Local server at `http://127.0.0.1:8000/api/v1/engagement/upload` for data logging.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up dlib Model**:
   - Download `shape_predictor_68_face_landmarks.dat` from the link above.
   - Extract and place it in the project root directory.
   - Update `model_path` in `main.py` if the file is stored elsewhere:
     ```python
     model_path = "path/to/shape_predictor_68_face_landmarks.dat"
     ```

4. **Install and Configure Ollama**:
   - Install Ollama: Follow instructions at [https://ollama.ai](https://ollama.ai).
   - Pull the Gemma 3 model:
     ```bash
     ollama pull gemma3:4b
     ```
   - Start the Ollama server:
     ```bash
     ollama run gemma3:4b
     ```

5. **Verify Webcam Access**:
   - Ensure your webcam is connected and accessible (test with Windows Camera app or similar).
   - Check Windows Privacy Settings: `Settings > Privacy > Camera > Allow apps to access your camera`.

## Usage
1. **Run the Application**:
   ```bash
   streamlit run main.py
   ```
   - The aSES engagement monitoring page opens at `http://localhost:8501`.
   - The chatbot assistant launches automatically as a subprocess at `http://localhost:8502`.

2. **Engagement Monitoring**:
   - Navigate to `http://localhost:8501`.
   - Fill in the sidebar form (Student Name, Matric Number, Course, Group, Module, Duration).
   - Click "Start Monitoring" to begin webcam-based engagement tracking.
   - View real-time video feed, engagement status, and timer.
   - Receive voice alerts if disengaged for too long.
   - At session end, see an engagement summary with a line chart.

3. **Chatbot Assistant**:
   - Click the sidebar link `[Open Chatbot Assistant]` to access `http://localhost:8502`.
   - Enter text queries or upload images (logged, not processed).
   - Interact with the Gemma 3-powered assistant for lecture help or engagement tips.
   - View conversation history in the UI.

4. **Stop the Application**:
   - Press `Ctrl+C` in the terminal to stop the main app.
   - The chatbot subprocess terminates automatically.

## Troubleshooting
- **Webcam Error (`videoio(MSMF): can't grab frame. Error: -1072873821`)**:
  - **Cause**: MSMF backend issues or webcam access conflict.
  - **Fix**:
    - Ensure no other apps (e.g., Zoom) are using the webcam.
    - Update webcam drivers via Device Manager.
    - The app uses `cv2.CAP_DSHOW` to avoid MSMF issues. If errors persist, try different camera indices (0, 1, 2) in `main.py`.
    - Test webcam with:
      ```python
      import cv2
      cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
      while cap.isOpened():
          ret, frame = cap.read()
          if not ret: print("Failed to grab frame"); break
          cv2.imshow("Test", frame)
          if cv2.waitKey(1) & 0xFF == ord('q'): break
      cap.release()
      cv2.destroyAllWindows()
      ```

- **Shape Predictor Error**:
  - **Cause**: Missing or incorrect path to `shape_predictor_68_face_landmarks.dat`.
  - **Fix**: Verify the file exists and update `model_path` in `main.py`.

- **Ollama Model Not Responding**:
  - **Cause**: Ollama server not running or model not pulled.
  - **Fix**:
    - Run `ollama run gemma3:4b` before starting the app.
    - Check `chatbot.log` for errors.
    - Use a smaller model (e.g., `gemma2:2b`) if memory is limited.

- **Server Connection Failure**:
  - **Cause**: Local server (`http://127.0.0.1:8000`) not running.
  - **Fix**: Start the server or check `engagement_data.csv` for locally saved data.

- **Performance Issues**:
  - **Cause**: High CPU/memory usage from dlib or Ollama.
  - **Fix**:
    - Reduce video resolution in `main.py` (e.g., `imutils.resize(frame, width=320)`).
    - Run Ollama on a separate machine if possible.
    - Monitor resources with Task Manager or `htop`.

## Limitations
- The chatbot does not process uploaded images, only logs their names (Gemma 3 lacks vision capabilities).
- Webcam compatibility varies; some devices may require alternative OpenCV backends (e.g., `cv2.CAP_V4L2` on Linux).
- Engagement detection relies on EAR, which may misclassify engagement in certain lighting or head pose conditions.

## Future Improvements
- Add vision support to the chatbot using a model like LLaVA.
- Implement head pose estimation for more accurate engagement detection.
- Save chat history to a file for persistence across sessions.
- Add a toggle to enable/disable the chatbot subprocess.

## License
This project is for educational purposes and not licensed for commercial use. Ensure compliance with licenses for dependencies (e.g., dlib, Ollama, Gemma 3).

## Contact
For issues or contributions, please contact the project maintainer or open an issue on the repository.