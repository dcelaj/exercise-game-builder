from enum import Enum, StrEnum
from pathlib import Path
import os

'''
CONTAINS ENUM CLASSES HOLDING VARIOUS OPTIONS USED THROUGHOUT THE PROJECT

The project mostly uses the .value so this is for readability more than anything. Also for tidying relative paths.
'''

# Resolving project file paths
#
#
# Resolving the root project directory (in this case, we are 2 layers in so we call parent twice)
root_dir = Path(__file__).resolve().parent.parent

# specifying subfolders from project root
lite_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_lite.task')
full_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_full.task')
heavy_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_heavy.task')

exercise_test = os.path.join(root_dir, 'models', 'exercise_model', 'randomforest_ex.joblib')
#
#
#

# Exercises supported for detection
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

# MediaPipe's result numbering
class Body_Parts(Enum): 
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

# Camera output options
class Cam_Style(Enum):
    SKELETON = 0            # Skeleton draws the landmark points and connecting lines in a black background
    NORMAL = 1              # Normal just shows the camera feed with no drawn annotations - saves some computing
    HYBRID = 2              # Camera feed with annotations drawn over - about same as skeleton w one less numpy op
    MASK = 3                # Most resource intensive, has mediapipe return an output mask of player's silhouette
    STILL_IMG = 4           # Least resource intensive, returns no camera feed - will allow player to import a pfp


class Model_Paths(StrEnum): 
    # Paths to MediaPipe model used
    MP_LITE = lite_mp_path
    MP_FULL = full_mp_path
    MP_HEAVY = heavy_mp_path

    # Paths to custom exercise model used
    EX_DEFAULT = exercise_test
