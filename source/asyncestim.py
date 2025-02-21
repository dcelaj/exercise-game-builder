# from enum import Enum
# from threading import Thread, Event
# from time import sleep

# import cv2
# from mediapipe.framework.formats import landmark_pb2
# from mediapipe import solutions
# import mediapipe as mp
# import numpy as np

'''
Asynchronous version of pose estim that uses mediapipe's livestream mode, 
to do later, too many threads to keep straight for now. Honestly I'm not
even sure it would be any faster. For now ignore this file.
'''
# # MediaPipe abbreviations
# BaseOptions = mp.tasks.BaseOptions
# PoseLandmarker = mp.tasks.vision.PoseLandmarker
# PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
# PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
# VisionRunningMode = mp.tasks.vision.RunningMode

# # TODO: see if more elegant way to handle path
# model_path = 'E:/Projects/exercise-testgame/models/mediapipe/pose_landmarker_full.task'

# # MediaPipe visualization functions 
# def draw_landmarks_on_image(rgb_image, detection_result):
#   '''
#   '''
#   pose_landmarks_list = detection_result.pose_landmarks
#   annotated_image = np.copy(rgb_image)

#   # Loop through the detected poses to visualize.
#   for idx in range(len(pose_landmarks_list)):
#     pose_landmarks = pose_landmarks_list[idx]

#     # Draw the pose landmarks.
#     pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
#     pose_landmarks_proto.landmark.extend([
#       landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
#     ])
#     solutions.drawing_utils.draw_landmarks(
#       annotated_image,
#       pose_landmarks_proto,
#       solutions.pose.POSE_CONNECTIONS,
#       solutions.drawing_styles.get_default_pose_landmarks_style())
#   return annotated_image

# # Return function for when async pose estim is  
# # done, which will update vars to show results
# # and trigger the exercise detection ML 
# def update_results(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
#     '''
#     '''
#     print('pose landmarker result: {}'.format(result))
#     # TODO: Use this callback to UPDATE THE CLASS VARIABLES

# # Setting the above function as the return func
# # and the model path and run mode
# options = PoseLandmarkerOptions(
#     base_options=BaseOptions(model_asset_path=model_path),
#     running_mode=VisionRunningMode.LIVE_STREAM,
#     result_callback=update_results)


# # Main pose estimation function
# def estimate_pose(cap):
#     with PoseLandmarker.create_from_options(options) as landmarker:
#         # Setup video feed
#         #cap = cv2.VideoCapture(0)
#         #temporary counter to stop infinite loop
#         counter = 0
#         mp_image = None

#         while cap.isOpened():
#             # Get frame and timestamp from video feed
#             ret, frame = cap.read()
#             timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

#             # Convert the frame received from OpenCV to a MediaPipe’s Image object.
#             frame.flags.writeable = False # first to delete if shit goes awry
#             mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

#             # Send live image data to perform pose landmarking asynchronously
#             landmarker.detect_async(mp_image, timestamp_ms)
#             frame.flags.writeable = True

#             # break out of loop
#             counter += 1
#             if counter > 100:
#                 break
#             if cv2.waitKey(10) & 0xFF == ord('q'):
#                 break
        
#         cap.release()
#         cv2.destroyAllWindows()

# class PoseEstimation(Thread):
#     '''
#     A dedicated pose estimation and exercise detection thread class, subclass of threading.Thread.

#     Reads camera input and performs passes of machine learning on the output all in its own thread.
#     '''

#     # READ-ONLY Public Variables
#     cap = None                      # Holds CV2's video capture feed
#     frame = None
#     image = None                    # Holds MP image info converted from a cap video feed frame
#     ret = None
#     results = None                  # Holds all the results of the MediaPipe inference
#     landmarks = None                # Can also be accessed by results.pose_landmarks.landmark
#     exercise_list = Enum(           # Holds an enum list of all available exercises
#     'Exercises', 
#     'JUMPING_JACK HIGH_KNEES LEG_RAISE ARMCIRCLES SQUAT DEADLIFT PLANK PUSHUP CRUNCH LAT_RAISE OVERHEAD_PRESS CURL TRICEP_EXTENSION')

#     # Re-Writable Public Variables
#     exercise = None                 # Can change DYNAMICALLY - corresponds to the exercise the level is detecting from the list
#     showcam = None                  # If false, only shows black screen instead of camera feed mirror

#     # Protected Variables
#     _stop_event = Event()           # Just an event flag for graceful exit

#     # Constructor & Inputs
#     def __init__(self, exercise=1, showcam=False):
#         Thread.__init__(self)
#         self.exercise = exercise
#         self.showcam = showcam

    
#     # Running the pose estimation followed by exercise detection in continuous loop
#     def run(self):
#         # Setup VIDEO FEED
#         self.cap = cv2.VideoCapture(0)

#         print("setup video")

#         while not self._stop_event.is_set() and self.cap.isOpened():
#             self.estimate_pose()
#             self.detect_exercise()

#         print(f"Thread finished")
#         return 0
    
#     # Changes the exercise being detected
#     def change_exercise(self, new_exercise):
#         self.exercise = new_exercise
    
#     # Gracefully exits
#     def stop(self):
#         self.cap.release()
#         self._stop_event.set()
