from enum import Enum
from threading import Thread, Event
from time import sleep

import cv2
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions
import mediapipe as mp
import numpy as np

# MediaPipe abbreviations
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# TODO: see if more elegant way to handle path
model_path = 'E:/Projects/exercise-testgame/models/mediapipe/pose_landmarker_full.task'

# MediaPipe visualization functions 
def draw_landmarks_on_image(rgb_image, detection_result):
  '''
  Draw pose tracking landmarks on any image
  '''
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

# MediaPipe Settings
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO)

# Main pose estimation function
def estimate_pose(cap, landmarker):
    # Get image frame and time from video feed
    ret, frame = cap.read()
    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

    # Convert the frame received from OpenCV to a MediaPipe’s Image object.
    frame.flags.writeable = False 
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

    # Send live image data to perform pose landmarking asynchronously
    pose_landmarker_result = landmarker.detect_for_video(mp_image, timestamp_ms)
    frame.flags.writeable = True 
    # The purpose of the two frame.flags lines is it supposedly forces py to work via reference
    # and makes it go faster. If stuff goes awry, those are the first two suspects to delete

    return mp_image, pose_landmarker_result

# Exercise detection using MediaPipe output
# TODO: write the damn function
def detect_exercise(ex):
    sleep(1)
    print(f"blorp {ex}")

class PoseEstimation(Thread):
    '''
    A dedicated pose estimation and exercise detection thread class, subclass of threading.Thread.

    Reads camera input and performs passes of machine learning on the output all in its own thread.
    '''

    # READ-ONLY Public Variables
    cap = None                      # Holds CV2's video capture feed
    image = None                    # Holds MP image info converted from a cap video feed frame
    mp_results = None               # Holds all the results of the MediaPipe inference
    ex_results = None               # Can also be accessed by results.pose_landmarks.landmark
    exercise_list = Enum(           # Holds an enum list of all available exercises
    'Exercises', 
    'JUMPING_JACK HIGH_KNEES LEG_RAISE ARMCIRCLES SQUAT DEADLIFT PLANK PUSHUP CRUNCH LAT_RAISE OVERHEAD_PRESS CURL TRICEP_EXTENSION')

    # Re-Writable Public Variables
    exercise = None                 # Can change DYNAMICALLY - corresponds to the exercise the level is detecting from the list
    showcam = None                  # If false, only shows black screen instead of camera feed mirror

    # Protected Variables
    _stop_event = Event()           # Just an event flag for graceful exit

    # Constructor & Inputs
    def __init__(self, exercise=1, showcam=False):
        Thread.__init__(self)
        self.exercise = exercise
        self.showcam = showcam

    
    # Running the pose estimation followed by exercise detection in continuous loop
    def run(self):
        # Setup VIDEO FEED
        self.cap = cv2.VideoCapture(0)

        # Create MediaPipe object and start detection loop
        with PoseLandmarker.create_from_options(options) as landmarker:
            while not self._stop_event.is_set() and self.cap.isOpened():
                # Perform pose estimation and store results
                temp_img, self.mp_results = estimate_pose(self.cap, landmarker)
                self.image = temp_img # TODO: delete after testing
                # Use results to draw the landmark, store that
                # TODO: add in option for blackout cam and no cam at all for faster speed
                #self.image = draw_landmarks_on_image(temp_img, self.mp_results)
                print(self.mp_results)

                # Perform exercise detection, store result
                # TODO: Write the detect exercise as an out of class function maybe make ex results a list and give it to func to pop to
                detect_exercise(self.exercise)

        print(f"Thread finished")
        return 0

    # Changes the exercise being detected
    def change_exercise(self, new_exercise):
        self.exercise = new_exercise
    
    # Gracefully exits
    def stop(self):
        self.cap.release()
        self._stop_event.set()
