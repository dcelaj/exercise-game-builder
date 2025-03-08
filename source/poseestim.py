### Imports and abbreviations
import enumoptions as op
from threading import Thread, Event, Lock
from collections import deque
from typing import Optional
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions
import mediapipe as mp

# MediaPipe abbreviations
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

import cv2
import numpy as np
import joblib
###

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

def exercise_specific_processing(ex):   
    # TODO: If you implement exercises needing special processing, use this and write a call in the detect exercise private func
    pass

# Main Pose Estimation & Exercise Detection Thread
class Pose_Estimation(Thread):
    '''
    A dedicated pose estimation and exercise detection thread class, subclass of threading.Thread.
    Reads camera input and performs passes of machine learning on the output all in its own thread.

    Only one of these threads should exist at a time (will eventually enforce singleton). Feel free
    to read the public variables at any time, or if you really care about preventing race conditions 
    use get_results (Python's Global Interpreter Lock makes this mostly unnecessary though)

    Arguments:
    - exercise: int
    - return_mask: bool

    READ-ONLY Public Variables: 
    - cap: cv2.VideoFeed
    - frame: ndarray
    - mp_image: ndarray
    - mp_result: MediaPipe Object
    - mp_mask: None
    - exercise: int
    - ex_results: deque

    Protected Variables:
    - _stop_event: Event (threading)
    - _m_updated: Event (threading)
    - _m_lock: Lock (threading)
    - _ex_model: JobLib Object
    - _options: MediaPipe Object
    - _exists: bool

    Example usage:
        import poseestim.py as pe
        t1 = pe.Pose_Estimation()
        print('Current estimated landmarks: ', t1.mp_results)
        print('Doing the exercise correctly?: ', bool(t1.ex_results[-1]))
    '''

    # Protected Class Variable - Singleton Pattern
    _exists = False                           # Is there already an instance of this class in existence? 

    # Constructor, Inputs, & Variables
    def __init__(self, exercise=op.Exercises.CRUNCH.value, return_mask=False, 
                 mp_model_path=op.Model_Paths.MP_FULL.value, ex_model_path=op.Model_Paths.EX_DEFAULT.value):
        # Calling Thread parent class constructor
        super().__init__()

        # Setting up variables
        self.return_mask = return_mask        # Not yet implemented

        # READ-ONLY Public Variables
        self.cap = None                       # Holds CV2's video capture feed object
        self.frame = None                     # Holds raw CV2 video frame
        self.mp_image = None                  # Holds MP image info converted from a cap video feed frame
        self.mp_results = None                # Holds all the results of the MediaPipe inference
        self.mp_mask = None                   # Holds body shape image mask returned by MediaPipe
        self.exercise = exercise              # Corresponds to the exercise the level is detecting from the list
        self.ex_results = deque(maxlen=32)    # Holds the most recent 32 results of exercise detection (last ~2 secs)

        # Protected variables
        self._stop_event = Event()            # Just an event flag for graceful exit
        self._options = PoseLandmarkerOptions(# MediaPipe settings
            base_options=BaseOptions(model_asset_path=mp_model_path),
            running_mode=VisionRunningMode.VIDEO)
        self._ex_model = joblib.load(         # Loading exercise model
            ex_model_path)
        self._m_updated = Event()            # Flag for if ex_model is safe to run (T) or is pending update (F)...
        self._m_updated.set()                # ...model update is rare, so putting mutex accquisition behind flag for speed
        self._m_lock = Lock()                # Mutex for updating exercise model, see above two variables
        Pose_Estimation._exists = True        # Singleton Pattern - so only one instance exists at a time
    
    # Pose Estimation Call
    def _estimate_pose(self, cap, landmarker):
        '''
        Uses the video feed capture and mediapipe landmarker objects (see 'def run(self):') to estimate pose and 
        body landmark position. "Private" function.

        Although this is technically an instance method, for data safety, it is being treated as an outside call. 
        This allows us to return the results and update the internal variables all at once. It is placed inside 
        the class purely for organizational reasons.

        Arguments: (besides self)
        - cap, a cv2.VideoCapture object
        - landmarker, a mediapipe model object
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
        if self.return_mask:
            mask = None
            # If you have an insanely fast computer and want to implement this, here
            # is where you'd parse out the mask from the results - don't forget to
            # go in __init__ func and add the extra argument to PoseLandmarkerOptions
            # output_segmentation_masks=self.return_mask
        else:
            mask = None

        # Return the results
        return cv_frame, mp_image, pose_landmarker_result, mask

    # Exercise Detection Function 
    def _detect_exercise(self, mp_rslt, exrcs):
        '''
        Just calls a cleanup function for data preprocessing, then calls the joblib RF model and
        feeds it the cleaned up data, then hands back the prediction to be appended to FIFO deque.
        "Private" function.

        Takes the mp results object as input. Yes this could have just used self., but this feels
        better for data safety convention.

        Arguments: (besides self)
        - mp_rslt, the mediapipe results object
        - exrcs, what exercise or movement is being detected
        '''
        # Check if the main thread wants to update the model
        if not self._m_updated.is_set():
            # Give permission to update
            self._m_lock.release()
            # Wait until finished updating
            self._m_updated.wait()
            # Regain control of mutex when update done
            self._m_lock.acquire()
        
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
        # Acquire lock - 99% of time will have lock
        self._m_lock.acquire()

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

        # Clean up
        print(f"Camera thread closed")
        self._m_lock.release()
        return 0
    
    #
    # Below this point are public functions - ones that are meant to be called repeatedly, anyway
    #

    # Dump all results in a thread safe way
    def get_results(self):
        '''
        Returns the camera frame (ndarray), the mediapipe results (its own object), the exercise detection
        results (deque), and the mask (None if show mask set to false, not implemented yet so always none)
        in a thread safe way. 
        
        However, in practice, you can just read these variables at any time directly since race conditions
        are not too troublesome in this context. If you need speed and don't care about race conditions,
        just access them like you would any class variable.

        No Arguments.
        '''

        # Make flag false to get thread to release lock
        self._m_updated.clear()
        # Wait for thread to give permission to update (since this func will be called from Main thread)
        self._m_lock.acquire()

        # Store all results in temporary variables
        frm = self.frame
        mp_rslts = self.mp_results
        ex_rslts = self.ex_results
        msk = self.mp_mask

        # Release lock and fix flag again
        self._m_lock.release()
        self._m_updated.set()

        return frm, mp_rslts, ex_rslts, msk
    
    # Get a specific result, like a body part
    def get_body_part(self, body_part=op.Body_Parts.NOSE.value, mp_rslts=None, safer=False):
        '''
        Returns xyz coordinates and visibility of a given body part from a mediapipe results object. 
        With no arguments, returns the nose. See enumoptions.py for list of body parts. 
        
        Accepts an int corresponding to the body part, a mediapipe object to parse (put None to get
        the most recent result), and a bool that forces this to be slower but thread safe if trying 
        to get most recent result.
        '''
        # If user doesn't input a specific result, grab most recent
        if mp_rslts is None and not safer:
            # Faster, technically not thread safe but Python's GIL makes this perfectly fine
            mp_rslts = self.mp_results
        elif mp_rslts is None and safer:
            # Fully thread safe, make flag false so cam thread gives up lock
            self._m_updated.clear()
            self._m_lock.acquire()
            # Store in temp variable
            mp_rslts = self.mp_results
            # Return lock and flag to how they were
            self._m_lock.release()
            self._m_updated.set()

        # Abbreviation for...
        pose_landmarks_list = mp_rslts.pose_landmarks     # the result list in the media pipe return

        # If no detection at all
        if (len(pose_landmarks_list) == 0):
            return (0.0, 0.0, 0.0), 0.0
        
        #
        pose_landmarks = pose_landmarks_list[0]           # I have no idea why they made this a 2d list
        
        # Parsing out coordinates and visibility
        x = pose_landmarks[body_part].x
        y = pose_landmarks[body_part].y
        z = pose_landmarks[body_part].z
        v = pose_landmarks[body_part].visibility

        # Returning as a tuple and a float
        return (x, y, z), v

    # Changes the exercise being detected and possibly the model
    def set_exercise(self, new_exercise: int):
        '''
        Update the exercise being detected. See Exercises in enumoptions.py for a list of possible inputs.
        '''
        # Make flag false to show model will be updating and not safe to use
        self._m_updated.clear()
        # Wait for thread to give permission to update (since this will be called from Main thread)
        self._m_lock.acquire()

        # Actually update the model, if new exercise calls for updating it
        if op.exercise_to_model[new_exercise] is not op.exercise_to_model[self.exercise]:
            self._ex_model = joblib.load(op.exercise_to_model[new_exercise])
        
        # Clear results for new data types to come through
        self.ex_results.clear()
        self.exercise = new_exercise

        # Finished - give back lock and set flag to let thread know model was updated (order is important)
        self._m_lock.release()
        self._m_updated.set()
    
    # Gracefully exits
    def stop(self):
        '''
        Gracefully terminates thread. Don't forget "del thread_name" to release name binding.
        '''
        self._stop_event.set()
        self.cap.release()
        Pose_Estimation._exists = False
