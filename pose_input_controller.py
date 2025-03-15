import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import cv2
import time
import numpy as np
from mediapipe.framework.formats import landmark_pb2
import sys
import keyboard
import subprocess
import pyttsx3

# -------------------------------
# Model and Camera Initialization
# -------------------------------
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task'
MODEL_PATH = 'pose_landmarker.task'


class PoseInputController:
    def __init__(self,
                 camera_width=320, camera_height=240,
                 left_threshold=0.3, right_threshold=1.0-0.3,
                 up_threshold=0.35, down_threshold=1.0-0.35,
                 single_trigger=True):
        """
        Initializes the pose input controller.

        Parameters:
          - camera_width, camera_height: resolution for the video capture.
          - left_threshold, right_threshold: normalized x boundaries for left/right events.
          - up_threshold, down_threshold: normalized y boundaries for up/down events.
          - single_trigger: if True, each event triggers only once per gesture.
        """
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.left_threshold = left_threshold
        self.right_threshold = right_threshold
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.single_trigger = single_trigger

        # text-to-speach flag
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Adjust speech speed if needed

        # Flags to allow single triggering per gesture
        self.triggered_right = False
        self.triggered_left = False
        self.triggered_up = False
        self.triggered_down = False

        # Event queue to hold input events
        self.events = []
        # Setup camera
        if sys.platform == "darwin":
            print("Running on macOS")
            self.cap = cv2.VideoCapture(1)
        elif sys.platform.startswith("win"):
            print("Running on Windows")
            self.cap = cv2.VideoCapture(0)
        else:
            print("Running on Linux")
            self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        print("Camera initialized")
        # print the acquired camera name
        print(self.cap.getBackendName())

        # Download model if not present
        if not os.path.exists(MODEL_PATH):
            print("Downloading model...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

        # Setup MediaPipe Pose Landmarker
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        def process_result(result: mp.tasks.vision.PoseLandmarkerResult, *args):
            self.latest_result = result

        self.latest_result = None
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=process_result,
            output_segmentation_masks=False  # disable to speed up processing
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

        # Define stick figure connections (for drawing)
        # Here we connect the nose (0) to shoulders (11 and 12) for the head,
        # then standard connections for arms, hips and legs.
        self.STICK_CONNECTIONS = [
            (0, 11), (0, 12),  # Head: nose to shoulders
            (11, 12),  # Shoulders
            (11, 13), (13, 15),  # Left arm
            (12, 14), (14, 16),  # Right arm
            (11, 23), (12, 24),  # Shoulders to hips
            (23, 24),  # Hips
            (23, 25), (25, 27),  # Left leg
            (24, 26), (26, 28)  # Right leg
        ]

    def speak(self, text):
        """
        Uses text-to-speech to read out the detected movement.
        """
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def draw_regions(self, image):
        """
        Draws translucent colored regions on the image:
          - Left region: left side (blue)
          - Right region: right side (green)
          - Up region: top (yellow)
          - Down region: bottom (red)
        """
        h, w, _ = image.shape
        # Define rectangle boundaries based on normalized thresholds.
        left_rect = (0, 0, int(self.left_threshold * w), h)
        right_rect = (int(self.right_threshold * w), 0, w, h)
        up_rect = (0, 0, w, int(self.up_threshold * h))
        down_rect = (0, int(self.down_threshold * h), w, h)

        # Colors (BGR)
        left_color = (255, 0, 0)  # Blue
        right_color = (0, 255, 0)  # Green
        up_color = (0, 255, 255)  # Yellow
        down_color = (0, 0, 255)  # Red

        overlay = image.copy()
        alpha = 0.3  # transparency factor

        cv2.rectangle(overlay, (left_rect[0], left_rect[1]), (left_rect[2], left_rect[3]), left_color, -1)
        cv2.rectangle(overlay, (right_rect[0], right_rect[1]), (right_rect[2], right_rect[3]), right_color, -1)
        cv2.rectangle(overlay, (up_rect[0], up_rect[1]), (up_rect[2], up_rect[3]), up_color, -1)
        cv2.rectangle(overlay, (down_rect[0], down_rect[1]), (down_rect[2], down_rect[3]), down_color, -1)

        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        return image

    def draw_stick_figure(self, image, pose_landmarks, color=(0, 255, 0), thickness=2, circle_radius=3):
        """
        Draws a simplified stick figure over the image using selected landmarks.
        """
        h, w, _ = image.shape
        landmark_coords = {}
        # Key landmarks for drawing (head, shoulders, arms, etc.)
        key_landmarks = {0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28}
        for idx, landmark in enumerate(pose_landmarks):
            x_px = int(landmark.x * w)
            y_px = int(landmark.y * h)
            landmark_coords[idx] = (x_px, y_px)
            if idx in key_landmarks:
                cv2.circle(image, (x_px, y_px), circle_radius, color, -1)
        for start_idx, end_idx in self.STICK_CONNECTIONS:
            if start_idx in landmark_coords and end_idx in landmark_coords:
                cv2.line(image, landmark_coords[start_idx], landmark_coords[end_idx], color, thickness)
        return image

    def check_inputs(self, pose_landmarks):
        """
        Checks the pose landmarks and triggers events based on screen regions.

        - For right/left, both wrists (landmarks 15 and 16) must be in the respective region.
        - For up/down, the nose (landmark 0) must be in the corresponding region.

        Each event is triggered only once per gesture if single_trigger is enabled.
        """
        # Use normalized coordinates for comparisons.
        right_trigger = False
        left_trigger = False
        up_trigger = False
        down_trigger = False

        # Ensure there are enough landmarks.
        if len(pose_landmarks) < 17:
            return

        # Retrieve key landmarks.
        left_wrist = pose_landmarks[15]
        right_wrist = pose_landmarks[16]
        nose = pose_landmarks[0]

        if left_wrist.x >= self.right_threshold and right_wrist.x >= self.right_threshold:
            right_trigger = True
        if left_wrist.x <= self.left_threshold and right_wrist.x <= self.left_threshold:
            left_trigger = True
        if nose.y <= self.up_threshold:
            up_trigger = True
        if nose.y >= self.down_threshold:
            down_trigger = True

        # Trigger events only once until gesture resets.
        if right_trigger and not self.triggered_right:
            self.triggered_right = True
            self.events.append("move_left")
            print("Triggered move_left")
            keyboard.press_and_release('left')
            self.speak("left")
        if not right_trigger:
            self.triggered_right = False

        if left_trigger and not self.triggered_left:
            self.triggered_left = True
            self.events.append("move_right")
            print("Triggered move_right")
            keyboard.press_and_release('right')
            self.speak("right")
        if not left_trigger:
            self.triggered_left = False

        if up_trigger and not self.triggered_up:
            self.triggered_up = True
            self.events.append("move_up")
            print("Triggered move_up")
            keyboard.press_and_release('up')
            self.speak("up")
        if not up_trigger:
            self.triggered_up = False

        if down_trigger and not self.triggered_down:
            self.triggered_down = True
            self.events.append("move_down")
            print("Triggered move_down")
            keyboard.press_and_release('down')
            self.speak("down")
        if not down_trigger:
            self.triggered_down = False

    def get_events(self):
        """
        Returns the list of triggered events and clears the event queue.
        """
        events = self.events.copy()
        self.events.clear()
        return events

    def run(self):
        """
        Main loop: capture frames, process pose detection, check for input events,
        draw the stick figure and colored regions, and display the video.
        """
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            # Convert frame for MediaPipe processing.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp = int(time.time() * 1000)
            self.landmarker.detect_async(mp_image, timestamp)

            # Copy frame for annotation and draw the trigger regions.
            annotated_frame = rgb_frame.copy()
            annotated_frame = self.draw_regions(annotated_frame)

            # If results are available, draw the stick figure and check inputs.
            if self.latest_result is not None:
                for pose_landmarks in self.latest_result.pose_landmarks:
                    self.check_inputs(pose_landmarks)
                    annotated_frame = self.draw_stick_figure(annotated_frame, pose_landmarks)

            display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
            cv2.imshow('Pose Input Detection', display_frame)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        self.cap.release()
        self.landmarker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controller = PoseInputController()
    controller.run()