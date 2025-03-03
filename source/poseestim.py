from enum import Enum, StrEnum
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

# MediaPipe visualization functions TODO: make some more fun customization options
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

# Enums for settings to be used in my custom class - recommend importing pose estim as pe and doing pe.Exercises.whatever
class Exercises(Enum): # Edit only needed if making new exercise
    JUMPING_JACK = 0 
    HIGH_KNEES = 1
    LEG_RAISE = 2
    ARMCIRCLES = 3
    SQUAT = 4
    DEADLIFT = 5
    PLANK = 6
    PUSHUP = 7
    CRUNCH = 8
    LAT_RAISE = 9
    OVERHEAD_PRESS = 10 
    CURL = 11
    TRICEP_EXTENSION = 12
class Body_Parts(Enum): # MediaPipe's result numbering
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
class Model_Paths(StrEnum): # Paths to MediaPipe model used - TODO: consider os.path.join('..', 'models', 'target_file.txt')
    LITE = 'E:/Projects/exercise-testgame/models/mediapipe/pose_landmarker_lite.task'
    FULL = 'E:/Projects/exercise-testgame/models/mediapipe/pose_landmarker_full.task'
    HEAVY = 'E:/Projects/exercise-testgame/models/mediapipe/pose_landmarker_heavy.task'

# Main Pose Estimation & Exercise Detection Thread
class Pose_Estimation(Thread):
    '''
    A dedicated pose estimation and exercise detection thread class, subclass of threading.Thread.
    Reads camera input and performs passes of machine learning on the output all in its own thread.
    '''

    # Protected Class Variable - Singleton Pattern
    _exists = False                           # Is there already an instance of this class in existence? 

    # Constructor & Inputs
    def __init__(self, exercise=Exercises.CRUNCH.value, showcam=False, model_path=Model_Paths.FULL.value):
        # Calling Thread constructor
        super().__init__()

        # Setting up variables
        self.exercise = exercise              # Can change DYNAMICALLY - corresponds to the exercise the level is detecting from the list
        self.showcam = showcam

        # READ-ONLY Public Variables
        self.cap = None                       # Holds CV2's video capture feed bject
        self.frame = None                     # Holds raw CV2 video frame
        self.mp_image = None                  # Holds MP image info converted from a cap video feed frame
        self.mp_results = None                # Holds all the results of the MediaPipe inference
        self.mp_mask = None                   # Holds body shape image mask returned by MediaPipe
        self.ex_results = None                # Can also be accessed by results.pose_landmarks.landmark

        # Protected variables
        self._stop_event = Event()            # Just an event flag for graceful exit
        self._options = PoseLandmarkerOptions(# MediaPipe settings
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO)
        Pose_Estimation._exists = True         # Singleton Pattern - so only one instance exists at a time
    
    # Main Pose Estimation Function TODO: 
    def _estimate_pose(self, cap, landmarker):
        '''
        Although this is technically an instance method, for data safety, it is being treated as a foreign call.
        This allows us to return the results and update the internal variables all at once.

        It is placed inside the class purely for organizational reasons.
        '''

        # Get image frame and time from video feed
        ret, cv_frame = cap.read()
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_frame)

        # Send live image data to perform pose landmarking - treating it as video
        # rather than live feed because blocking makes things simpler than async
        pose_landmarker_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # TODO: Add image mask option
        mask = None

        # Return the results
        return cv_frame, mp_image, pose_landmarker_result, mask

    # Main Exercise Detection Function TODO: 
    def _detect_exercise(self):
        '''
        TODO: make the damn model
        # TODO: Perform exercise detection, store classification results in a FIFO buffer list
        ex_results, which can then be read, if x most recent results same, then det is confirm
        '''
        print("TODO")
        dummy = [True, True, True, True, True]
        return dummy
    
    #
    # Running the pose estimation followed by exercise detection in continuous loop
    #
    def run(self):
        # Set up video feed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Create MediaPipe object
        with PoseLandmarker.create_from_options(self._options) as landmarker:
            # Start detection loop
            while not self._stop_event.is_set() and self.cap.isOpened():
                # Perform pose estimation and store updated results
                self.frame, self.mp_image, self.mp_results, self.mp_mask = self._estimate_pose(self.cap, landmarker)
                
                # Use those results to detect if an exercise is being properly done
                self.ex_results = self._detect_exercise()

        print(f"Thread finished")
        return 0
    
    # Get annotate image, mask, or just draw on pure black TODO: move or make call here
    def get_annotated_image(self):
        '''
        note that if you want non annotated or raw data, just do instance_name.var, this only to perform annottn
        see class explanation or constructor for list of vars you can access
        '''
        # TODO: write this, check showcam variable too
        # TODO: ADD OPTION FOR GETTING IMG MASK TOO
        print("TODO")
    
    # Get a specific result, like a body part TODO: this
    def get_body_part(self):
        '''
        Explain enum options - note in the future you can just instance_name.exercise to get/set
        '''
        # TODO: write this
        print("TODO")

    # Changes the exercise being detected
    def set_exercise(self, new_exercise):
        '''
        Explain enum options - note in the future you can just instance_name.exercise to get/set if you know the options
        '''
        self.exercise = new_exercise
    
    # Gracefully exits
    def stop(self):
        '''
        Gracefully terminates thread. Don't forget "del thread_name" to release name binding.
        '''
        self.cap.release()
        self._stop_event.set()
        Pose_Estimation._exists = False
