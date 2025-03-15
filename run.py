import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import cv2
import time

URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task'
MODEL_PATH = 'pose_landmarker.task'

# Download model if it doesn't exist
if not os.path.exists(MODEL_PATH):
    print('Downloading model...')
    urllib.request.urlretrieve(URL, MODEL_PATH)
    print('Model downloaded to', MODEL_PATH)

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")
print('Camera found')

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Callback function to process results
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print('Pose landmarker result received')

def get_frame_timestamp_ms():
    return int(round(time.time() * 1000))

# Create pose landmarker instance
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        # Process image asynchronously
        landmarker.detect_async(mp_image, get_frame_timestamp_ms())

        # Convert annotated image back to BGR before displaying
        annotated_image = cv2.cvtColor(mp_image.numpy_view(), cv2.COLOR_RGB2BGR)

        # Display the annotated image
        cv2.imshow('MediaPipe Pose Landmarker', annotated_image)

        # Break loop if 'q' is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
