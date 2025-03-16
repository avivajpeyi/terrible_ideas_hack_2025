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

if sys.platform == "darwin":
    print("Running on macOS")
elif sys.platform.startswith("win"):
    print("Running on Windows")
else:
    print("Running on Linux")

# -------------------------------
# Model and Camera Initialization
# -------------------------------
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task'
MODEL_PATH = 'pose_landmarker.task'

class PoseInputController:
    def __init__(self,
                 camera_width=320, camera_height=240,
                 left_threshold=0.3, right_threshold=1.0-0.3,
                 up_threshold=0.35, down_threshold=1.0-0.25,
                 single_trigger=True):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.left_threshold = left_threshold
        self.right_threshold = right_threshold
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.single_trigger = single_trigger

        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)

        self.triggered_right = False
        self.triggered_left = False
        self.triggered_up = False
        self.triggered_down = False
        self.current_key = None  # Track currently pressed key

        self.events = []
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        print("Camera initialized")

        if not os.path.exists(MODEL_PATH):
            print("Downloading model...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

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
            output_segmentation_masks=False
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

        self.STICK_CONNECTIONS = [
            (0, 11), (0, 12), (11, 12),
            (11, 13), (13, 15), (12, 14),
            (14, 16), (11, 23), (12, 24),
            (23, 24), (23, 25), (25, 27),
            (24, 26), (26, 28)
        ]

    def speak(self, text):
        # self.tts_engine.say(text)
        # self.tts_engine.runAndWait()
        pass

    def draw_regions(self, image):
        h, w, _ = image.shape
        left_rect = (0, 0, int(self.left_threshold * w), h)
        right_rect = (int(self.right_threshold * w), 0, w, h)
        up_rect = (0, 0, w, int(self.up_threshold * h))
        down_rect = (0, int(self.down_threshold * h), w, h)

        overlay = image.copy()
        alpha = 0.3
        cv2.rectangle(overlay, (left_rect[0], left_rect[1]), (left_rect[2], left_rect[3]), (255, 0, 0), -1)
        cv2.rectangle(overlay, (right_rect[0], right_rect[1]), (right_rect[2], right_rect[3]), (0, 255, 0), -1)
        cv2.rectangle(overlay, (up_rect[0], up_rect[1]), (up_rect[2], up_rect[3]), (0, 255, 255), -1)
        cv2.rectangle(overlay, (down_rect[0], down_rect[1]), (down_rect[2], down_rect[3]), (0, 0, 255), -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
        return image

    def draw_stick_figure(self, image, pose_landmarks, color=(0, 255, 0), thickness=2, circle_radius=3):
        h, w, _ = image.shape
        landmark_coords = {}
        key_landmarks = {0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28}
        for idx, landmark in enumerate(pose_landmarks):
            x_px = int(landmark.x * w)
            y_px = int(landmark.y * h)
            landmark_coords[idx] = (x_px, y_px)
            if idx in key_landmarks:
                cv2.circle(image, (x_px, y_px), circle_radius, color, -1)
            if idx ==0:
                cv2.circle(image, (x_px, y_px), circle_radius, (255,0,0), -1)
        for start_idx, end_idx in self.STICK_CONNECTIONS:
            if start_idx in landmark_coords and end_idx in landmark_coords:
                cv2.line(image, landmark_coords[start_idx], landmark_coords[end_idx], color, thickness)
        return image

    def check_inputs(self, pose_landmarks):
        right_trigger = False
        left_trigger = False
        up_trigger = False
        down_trigger = False

        if len(pose_landmarks) < 17:
            return

        left_wrist = pose_landmarks[15]
        right_wrist = pose_landmarks[16]
        nose = pose_landmarks[0]

        # if left_wrist.x >= self.right_threshold and right_wrist.x >= self.right_threshold:
        #     right_trigger = True
        # if left_wrist.x <= self.left_threshold and right_wrist.x <= self.left_threshold:
        #     left_trigger = True
        if nose.x >= self.right_threshold:
            right_trigger = True
        if nose.x <= self.left_threshold:
            left_trigger = True
        if nose.y <= self.up_threshold:
            up_trigger = True
        if nose.y >= self.down_threshold:
            down_trigger = True

        # Right trigger moves left
        if right_trigger and not self.triggered_right:
            if self.current_key is not None:
                keyboard.release(self.current_key)
            keyboard.press('left')
            self.current_key = 'left'
            self.events.append("move_left")
            print("Triggered move_left")
            self.speak("left")
            self.triggered_right = True
        if not right_trigger:
            self.triggered_right = False

        # Left trigger moves right
        if left_trigger and not self.triggered_left:
            if self.current_key is not None:
                keyboard.release(self.current_key)
            keyboard.press('right')
            self.current_key = 'right'
            self.events.append("move_right")
            print("Triggered move_right")
            self.speak("right")
            self.triggered_left = True
        if not left_trigger:
            self.triggered_left = False

        # Up trigger
        if up_trigger and not self.triggered_up:
            if self.current_key is not None:
                keyboard.release(self.current_key)
            keyboard.press('up')
            self.current_key = 'up'
            self.events.append("move_up")
            print("Triggered move_up")
            self.speak("up")
            self.triggered_up = True
        if not up_trigger:
            self.triggered_up = False

        # Down trigger
        if down_trigger and not self.triggered_down:
            if self.current_key is not None:
                keyboard.release(self.current_key)
            keyboard.press('down')
            self.current_key = 'down'
            self.events.append("move_down")
            print("Triggered move_down")
            self.speak("down")
            self.triggered_down = True
        if not down_trigger:
            self.triggered_down = False

    def get_events(self):
        events = self.events.copy()
        self.events.clear()
        return events

    def run(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp = int(time.time() * 1000)
            self.landmarker.detect_async(mp_image, timestamp)

            annotated_frame = rgb_frame.copy()
            annotated_frame = self.draw_regions(annotated_frame)

            if self.latest_result is not None:
                for pose_landmarks in self.latest_result.pose_landmarks:
                    self.check_inputs(pose_landmarks)
                    annotated_frame = self.draw_stick_figure(annotated_frame, pose_landmarks)

            display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
            cv2.imshow('Pose Input Detection', display_frame)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        # Cleanup
        self.cap.release()
        self.landmarker.close()
        cv2.destroyAllWindows()
        if self.current_key is not None:
            keyboard.release(self.current_key)

if __name__ == "__main__":
    controller = PoseInputController(single_trigger=False)
    controller.run()