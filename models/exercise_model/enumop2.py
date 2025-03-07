from enum import StrEnum
from pathlib import Path
import os

# finding the root project directory (in this case, we are 3 layers in so we call parent thrice)
root_dir = Path(__file__).resolve().parent.parent.parent

# specifying subfolders from project root
lite_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_lite.task')
full_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_full.task')
heavy_mp_path = os.path.join(root_dir, 'models', 'mediapipe', 'pose_landmarker_heavy.task')


class Model_Paths(StrEnum): 
    # Paths to MediaPipe model used
    MP_LITE = lite_mp_path
    MP_FULL = full_mp_path
    MP_HEAVY = heavy_mp_path

    # THE ONE BEING USED IN data_gatherer.py IS MP_FULL

    # By the way, enumoptions.py in the source folder
    # servers a similar purpose - check that out if
    # you're getting file path errors.

