import enumoptions as op
from threading import Thread, Event
from collections import deque
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions
import mediapipe as mp
import cv2
import numpy as np
import joblib

# MediaPipe abbreviations
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

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

# DATA CLEANUP AND PREPROCESSING FUNCTION - making MP's esoteric return readable for the RF model
def preprocess(result):
    '''
    Reformats **MediaPipe Results object** into ordered list of numbers. If no
    detection, returns None, otherwise returns a list.

    Might be worth adding in a check for head visibility (points 1 thru 10) and
    discarding them if too low. The BlazePose neural network architecture that
    MediaPipe relies on uses face detection as a proxy for person detection, so
    points that can't detect a face may be unreliable.  
    '''
    # Abbreviation for...
    body_pt = mp.solutions.pose.PoseLandmark        # the body landmark enumerations in mediapipe
    pose_landmarks_list = result.pose_landmarks     # the result list in the media pipe return
    # Values our model will ignore - basically eyes, lips, hands, and feet
    ignore = [1, 2, 3, 4, 5, 6, 9, 10, 17, 18, 19, 20, 21, 22, 29, 30, 31, 32]
    # What we return
    parsed_list = []

    # INPUT HANDLING AND DATA DISCARDING 
    # TODO: Implement discarding the invisible head data - have a lot of pts to check, 0-10
    # Maybe for efficiency only check nose vis (point 0) 
    if (len(pose_landmarks_list) == 0) or (False):
        return None

    # Parsing the results object that google has insanely poor documentation for
    # to extract the landmark values we're interested int
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]   # for some god unknown reason it's a 2d list with only one column

        # Loop through the inner list of landmarks and add each value to the list
        for part in body_pt:
            # Only the values we care about
            if part.value not in ignore:
                parsed_list.append(pose_landmarks[part.value].x)
                parsed_list.append(pose_landmarks[part.value].y)
                parsed_list.append(pose_landmarks[part.value].z)
                parsed_list.append(pose_landmarks[part.value].visibility)
            else:
                pass
    
    # Return simple list of numbers corresponding to [x coord, y coord, visibility, x coord, y coord, visibility...]
    # each body point landmark corresponding to some four consecutive values
    return parsed_list

def exercise_specific_processing(ex):   #TODO: delete this and incorproate support for switching exercise model mid game
    # TODO: actually incorporate some exercise specific stuff, whether it be switching the model or preprocessing
    # TODO: should also probably alter the other funcs to accommodate this instead of making this whole new func
    # TODO: It's moreso a reminder than anything else
    pass

# Main Pose Estimation & Exercise Detection Thread
class Pose_Estimation(Thread):
    '''
    A dedicated pose estimation and exercise detection thread class, subclass of threading.Thread.
    Reads camera input and performs passes of machine learning on the output all in its own thread.

    Arguments:
    - exercise: 
    READ-ONLY Public Variables:
    Protected Variables:
    '''

    # Protected Class Variable - Singleton Pattern
    _exists = False                           # Is there already an instance of this class in existence? 

    # Constructor, Inputs, & Variables
    def __init__(self, exercise=op.Exercises.CRUNCH.value, cam_style=op.Cam_Style.SKELETON.value, 
                 mp_model_path=op.Model_Paths.MP_FULL.value, ex_model_path=op.Model_Paths.EX_DEFAULT.value):
        # Calling Thread parent class constructor
        super().__init__()

        # Setting up variables
        self.exercise = exercise              # Can change DYNAMICALLY - corresponds to the exercise the level is detecting from the list
        self.cam_style = cam_style

        # READ-ONLY Public Variables
        self.cap = None                       # Holds CV2's video capture feed bject
        self.frame = None                     # Holds raw CV2 video frame
        self.mp_image = None                  # Holds MP image info converted from a cap video feed frame
        self.mp_results = None                # Holds all the results of the MediaPipe inference
        self.mp_mask = None                   # Holds body shape image mask returned by MediaPipe
        self.ex_results = deque(maxlen=32)    # Holds the most recent 32 results of exercise detection (last ~2 secs)

        # Protected variables
        self._stop_event = Event()            # Just an event flag for graceful exit
        self._ex_model = joblib.load(         # Loading exercise model
            ex_model_path)
        self._options = PoseLandmarkerOptions(# MediaPipe settings
            base_options=BaseOptions(model_asset_path=mp_model_path),
            running_mode=VisionRunningMode.VIDEO)
        Pose_Estimation._exists = True        # Singleton Pattern - so only one instance exists at a time
    
    # Pose Estimation Call
    def _estimate_pose(self, cap, landmarker):
        '''
        Uses the video feed capture and mediapipe landmarker objects (see 'def run(self):') to estimate pose and 
        body landmark position.

        Although this is technically an instance method, for data safety, it is being treated as an outside call. 
        This allows us to return the results and update the internal variables all at once. It is placed inside 
        the class purely for organizational reasons.
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
        if self.cam_style == op.Cam_Style.MASK.value:
            mask = None
        else:
            mask = None

        # Return the results
        return cv_frame, mp_image, pose_landmarker_result, mask

    # Exercise Detection Function 
    def _detect_exercise(self, mp_rslt, exrcs):
        '''
        Just calls a cleanup function for data preprocessing, then calls the joblib RF model and
        feeds it the cleaned up data. Then hands back the prediction to be appended to FIFO deque

        Takes the mp results object as input. Yes this could have just used self., but this feels
        better for data safety convention.
        '''
        # TODO: Incorporate ability to switch between exercise model mid game
        
        # Clean up MP results format
        clean = preprocess(mp_rslt)

        # Check if there was a detection, then feed into model to get prediction
        if clean is not None:
            # making into numpy array so it can be fed into model and reshape to show single sample
            input = np.array(clean).reshape(1, -1) 
            prediction = self._ex_model.predict(input)
        else:
            # If nothing could be detected, manually make prediction false
            prediction = 0
        return prediction
    
    # Main Function - Running the pose estimation followed by exercise detection in continuous loop
    def run(self):
        # Set up video feed
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Create MediaPipe landmarker object (initializes WASM runtime then makes class isntance)
        with PoseLandmarker.create_from_options(self._options) as landmarker:
            # Start detection loop
            while not self._stop_event.is_set() and self.cap.isOpened():
                # Perform pose estimation and store updated results
                self.frame, self.mp_image, self.mp_results, self.mp_mask = self._estimate_pose(self.cap, landmarker)
                
                # Use those results to detect if an exercise is being properly done
                predict = self._detect_exercise(self.mp_results, self.exercise)
                self.ex_results.append(predict)

        print(f"Thread finished")
        return 0
    
    #
    # Below this point are public functions - ones that are meant to be called repeatedly, anyway
    #

    # Dump all results (mainly for troubleshooting)
    def get_results(self):
        '''
        EXPLAIN THAT YOU SHOULD JUST ACCESS THE INSTANCE VARIABLES DIRECTLY
        this is more for troubleshooting, but it does return the results
        also explain if you want drawing/annotation, look to helpers for custom, 
        or maybe just use the mediapipe default global function from this file - not ran from thread, just the global func
        '''
        # TODO: write this, check showcam variable too
        # TODO: ADD OPTION FOR GETTING IMG MASK TOO
        print("TODO")
    
    # Get a specific result, like a body part TODO: this
    def get_body_part(self, body_part=op.Body_Parts.NOSE.value):
        '''
        Explain enum options - and return specific body part coordinate - default returns nose
        So levels.py user won't have to deal with mediapipe's esoteric formatting and documentation
        '''
        # TODO: write this
        print("TODO")

    # Changes the exercise being detected
    def set_exercise(self, new_exercise):
        '''
        Explain enum options and return data types depending on result
        also explain this just does an extra clear, you can set thread1.exercise directly
        '''
        # Clear results for new data types to come through
        self.ex_results.clear()
        self.exercise = new_exercise
    
    # Gracefully exits
    def stop(self):
        '''
        Gracefully terminates thread. Don't forget "del thread_name" to release name binding.
        '''
        self.cap.release()
        self._stop_event.set()
        Pose_Estimation._exists = False
