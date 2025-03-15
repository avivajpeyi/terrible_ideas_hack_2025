import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import cv2
import time

URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task'
MODEL_PATH = 'pose_landmarker.task'

# Download model if needed
if not os.path.exists(MODEL_PATH):
    print('Downloading model...')
    urllib.request.urlretrieve(URL, MODEL_PATH)

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")
print("Camera initialized")

# MediaPipe configuration
mp_pose = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Shared variable for results
latest_result = None


def process_result(result: mp.tasks.vision.PoseLandmarkerResult, *args):
    global latest_result
    latest_result = result


options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_poses=1,  # Detect up to 1 poses (inncrease for more people)
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    result_callback=process_result,
    output_segmentation_masks=True
)

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            break

        # Convert and process frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Get timestamp and process
        timestamp = int(time.time() * 1000)
        landmarker.detect_async(mp_image, timestamp)

        # Draw landmarks if available
        if latest_result:
            annotated_image = rgb_frame.copy()
            for pose_landmarks in latest_result.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    mp_drawing_styles.get_default_pose_landmarks_style()
                )

            # Convert back to BGR for display
            display_frame = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
            cv2.imshow('Pose Detection', display_frame)
        else:
            cv2.imshow('Pose Detection', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

print("Quit")
cap.release()
cv2.destroyAllWindows()
