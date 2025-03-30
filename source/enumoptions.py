from enum import Enum, StrEnum
from pathlib import Path
import os

'''
CONTAINS ENUM CLASSES HOLDING VARIOUS OPTIONS USED THROUGHOUT THE PROJECT

The project mostly uses the .value so this is for readability more than anything. Also for tidying relative paths.
'''

# Resolving project file paths:
# Root project directory (in this case, we are 2 layers in so we call parent twice)
root_dir = Path(__file__).resolve().parent.parent
# Now we can specify subfolders relative to project root

# Reading config file
# TODO add some code reading the config and resolving any relevant paths 

# Exercises supported for detection (exercises being used broadly to mean any pose or movement)
class Exercises(Enum): # Edit if making new exercise
    DEFAULT = 0 

    HIGH_KNEES = 1
    SQUAT = 2

    CRUNCH = 3
    PLANK = 4
    PUSHUP = 5

    CAST_SPELL = 6
    SWING_SWORD = 7

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

# Adding the model paths to an enum for consistency
class Model_Paths(StrEnum): 
    # Paths to MediaPipe model used
    MP_LITE = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_lite.task')
    MP_FULL = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_full.task')
    MP_HEAVY = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_heavy.task')

    # Paths to custom exercise model used
    EX_DEFAULT = os.path.join(root_dir, 'models', 'exercise_model', 'randomforest_ex.joblib')
    
    KNEES_N_LEGS = os.path.join(root_dir, 'models', 'exercise_model', 'rf_knees_n_legs.joblib')
    SIT_N_PUSHUP = os.path.join(root_dir, 'models', 'exercise_model', 'rf_sit_n_pushup.joblib')
    HACK_N_SLASH = os.path.join(root_dir, 'models', 'exercise_model', 'rf_hack_n_slash.joblib')

# Finally, a dict mapping given exercises to a model. Sometimes one model can be used for multiple things
# but you still want them to be different labels - like if you're making an RPG, swinging a sword is the
# same motion as swinging a hammer, but you probably want the game to treat them differently.
exercise_to_model = {
    Exercises.DEFAULT.value: Model_Paths.EX_DEFAULT.value,

    Exercises.HIGH_KNEES.value: Model_Paths.KNEES_N_LEGS.value,
    Exercises.SQUAT.value: Model_Paths.KNEES_N_LEGS.value,

    Exercises.CRUNCH.value: Model_Paths.SIT_N_PUSHUP.value,
    Exercises.PLANK.value: Model_Paths.SIT_N_PUSHUP.value,
    Exercises.PUSHUP.value: Model_Paths.SIT_N_PUSHUP.value,

    Exercises.CAST_SPELL.value: Model_Paths.HACK_N_SLASH.value,
    Exercises.SWING_SWORD.value: Model_Paths.HACK_N_SLASH.value,
}
