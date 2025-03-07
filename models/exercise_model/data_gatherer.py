import mediapipe as mp
import cv2
import csv
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QSlider, QFileDialog)
from PySide6.QtGui import QImage, QPixmap
import enumop2
# Windows specific import to play beeps on countdown - playsound would also work but i dont have the wav files for pure beeps
try:
    import winsound
except:
    pass

# MediaPipe File Paths
MP_LITE = enumop2.Model_Paths.MP_LITE.value
MP_FULL = enumop2.Model_Paths.MP_FULL.value
MP_HEAVY = enumop2.Model_Paths.MP_HEAVY.value

# DATA CLEANUP AND PREPROCESSING FUNCTION - IMPORTANT
def preprocess(result):
    '''
    Reformats data into ordered list of numbers to be put into a csv.

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

# Just an append convenience function
def append_list_to_csv(file_path, list_data):
    '''
    Appends a list as a new row to an existing CSV file.
    '''
    try:
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(list_data)
    except Exception as e:
        print(f"An error occurred: {e}")
# Just a clear file convenience function
def clear_csv(file_path):
    '''
    Clears a given file
    '''
    if not file_path.lower().endswith('.csv'):
            print('ONLY CSV FILES FOR NOW')
            return
    try:
        with open(file_path, 'w') as file:
            file.write('')
        print(f"CSV file '{file_path}' cleared successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


#
#
#
# Mess below, scroll at your own risk. Any function you'd be interested in changing is probably above.
#
#
#

# Global Vars
width = 0
height = 0

# MediaPipe abbreviations
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# MediaPipe settings
options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MP_FULL),
            running_mode=VisionRunningMode.VIDEO)

# INTRO TEXT
par1a = '<b>SMALL MINI APP TO AID IN DATA GATHERING TO TRAIN RF MODEL WITH POSES.</b>'
par1b = '<br><b>After you gather the data with this app, open randomforest_creator.py, change the \'csv0\' \'csv1\' \'csv2\''
par1c = ' vars to your csv file paths, and run it! Extra information is in the code comments!</b><br>'
par1 = par1a + par1b + par1c
par2a = '\'Start Countdown\' starts a 5s countdown, showing a few frames of camera view to make sure you position yourself properly. '
par2b ='It then stops updating camera but starts collecting pose data (excluding fingers and face), appending it to a file. <br>'
par2 = par2a + par2b
par3 = 'Data points slider controls amount of data points collected <b>per button press.</b> (Aim for 500 per category in total.)<br>'
par4a = 'Category button controls which file the pose data is appended to, each file meant to hold data for a different category. '
par4b = 'Click the button to bring up the file dialog and choose a CSV file to store the data in. Click clear to clear selected file.'
par4 = par4a + par4b

# Actual windowed app
class MyApp(QWidget):
    '''
    SMALL MINI APP TO AID IN DATA GATHERING TO TRAIN ML MODEL WITH POSES

    Starts a countdown for you to get into position, showing a few frames of camera view to make sure you position properly.
    Stops updating camera but starts collecting pose data, appending it to a file.

    Data points slider controls how many data points are collected per button press.

    Category drop down controls which file the pose data is appended to, meant to correspond to a different category.
    '''
    global width
    global height

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Setting up video feed, reading one frame 
        self.cap = None

        # Setting up app window and layout
        self.setWindowTitle('POSE DATA GATHERER')
        self.layout = QVBoxLayout()

        # Display App Info Text
        self.about = QLabel('About:', self)
        self.layout.addWidget(self.about)
        self.intro = QTextEdit(self)
        self.intro.setReadOnly(True)
        self.intro.append(par1)
        self.intro.append(par2)
        self.intro.append(par3)
        self.intro.append(par4)
        self.layout.addWidget(self.intro)

        # Making a horizontal organization for options
        self.opt = QHBoxLayout()

        # Slider for data point
        self.slider_layout = QVBoxLayout()
        self.datadesc = QLabel('Num. of data points to gather:', self)
        self.slider_layout.addWidget(self.datadesc)
        self.datalabel = QLabel('500', self)
        self.slider_layout.addWidget(self.datalabel)
        self.iters = 500
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setSingleStep(50)
        self.slider.setMinimum(50)
        self.slider.setMaximum(1500)
        self.slider.setValue(500)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self.slide)
        self.slider_layout.addWidget(self.slider)
        self.opt.addLayout(self.slider_layout)

        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.VLine)  
        self.sep.setFrameShadow(QFrame.Sunken)
        self.opt.addWidget(self.sep)

        # File for category
        self.cat_layout = QVBoxLayout()
        self.filelabel = QLabel('Select a CSV file for the category of data being gathered:', self)
        self.filebutt = QPushButton('No Category File Selected', self)
        self.filebutt.pressed.connect(self.select_file)
        self.file = None
        self.cat_layout.addWidget(self.filelabel)
        self.cat_layout.addWidget(self.filebutt)

        # Clear button
        self.clrbtt = QPushButton('DELETE FILE CONTENTS')
        self.clrbtt.clicked.connect(lambda: clear_csv(self.file))
        self.cat_layout.addWidget(self.clrbtt)

        self.opt.addLayout(self.cat_layout)
        self.layout.addLayout(self.opt)
        

        # Horizontal line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)  
        self.separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.separator)

        # Start Countdown Label
        self.label = QLabel('Press the button to start the countdown', self)
        self.layout.addWidget(self.label)

        # Displaying frame we read, with a black placeholder image
        self.img = QLabel()
        placeholder = QImage(250, 250, QImage.Format_BGR888)
        placeholder.fill(Qt.black)
        self.img.setPixmap(QPixmap.fromImage(placeholder))
        self.layout.addWidget(self.img)
        
        # START COUNTDOWN BUTTON
        self.button = QPushButton('Start Countdown', self)
        self.button.clicked.connect(self.start_countdown)
        self.layout.addWidget(self.button)

        # Quit Button
        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.quit_app)
        self.layout.addWidget(self.quit_button)
        
        # Adding everything to layout and resize
        self.setLayout(self.layout)
        self.resize(int(width*0.35), int(height*0.85))
        # Adding a timer for the countdown to update
        self.countdown_value = 5
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
    
    # Starting countdown timer and camera
    def start_countdown(self):
        # Init camera
        self.cap = cv2.VideoCapture(0)

        # Update image
        ret, new_frame = self.cap.read()
        new_frame = cv2.resize(new_frame, (0, 0), fx= 0.8, fy= 0.8)
        self.image = QImage(new_frame, new_frame.shape[1], new_frame.shape[0], 
            new_frame.strides[0], QImage.Format_BGR888)
        self.img.setPixmap(QPixmap.fromImage(self.image))

        # Start coutdown timer
        self.countdown_value = 5
        self.timer.start(1000)

    # Updating countdown from timer signal
    def update_countdown(self):
        if self.countdown_value > 0:
            # Update label and countdown value
            self.label.setText(f'Countdown: {self.countdown_value} seconds')
            self.countdown_value -= 1

            # Update image label
            ret, new_frame = self.cap.read()
            new_frame = cv2.resize(new_frame, (0, 0), fx= 0.8, fy= 0.8)
            self.image = QImage(new_frame, new_frame.shape[1], new_frame.shape[0], 
                new_frame.strides[0], QImage.Format_BGR888)
            self.img.setPixmap(QPixmap.fromImage(self.image))

            # play a beep async if on windows - do nothing if not
            try:
                winsound.Beep(440, 100)
            except:
                pass
        else: # On finishing
            self.timer.stop()
            self.label.setText('DATA GATHERING FINISHED!')

            # Create MediaPipe landmarker object 
            with PoseLandmarker.create_from_options(options) as landmarker:
                # start a loop gathering iterations amount of data
                self.gather_data(self.cap, landmarker, self.iters, self.file)
            
            # Letting user know it's done with a sound notif if on windows
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass
    
    # Gathering data using the mediapipe model
    def gather_data(self, cap, landmarker, iterations, data_file):
        # input checking
        if data_file is None:
            self.label.setText('NO FILE SELECTED')
            return
        elif not data_file.lower().endswith('.csv'):
            self.label.setText('ONLY CSV FILES ACCEPTED AS OF NOW')
            return

        # iterations == points of data
        for i in range(iterations):
            # Get image frame and time from video feed
            ret, cv_frame = cap.read()
            timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

            # Convert the frame received from OpenCV to a MediaPipe’s Image object.
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_frame)

            # Send live image data to perform pose landmarking - treating it as video
            # rather than live feed because blocking makes things simpler than async
            pose_landmarker_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            # Clean up formatting
            clean_data = preprocess(pose_landmarker_result)
            # Append to csv file
            append_list_to_csv(data_file, clean_data)
    
    # Controlling slider variable
    def slide(self, value):
        self.datalabel.setText(str(value))
        self.iters = int(value)
    # Select file directory
    def select_file(self):
        root_dir = str(enumop2.root_dir)
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open Data File"), root_dir, self.tr("Image Files (*.csv *.txt *.xml)"))
        self.filebutt.setText(fileName[0])
        self.file = fileName[0]
        

    # Controlling drop down options
    
    # Gracefully quitting the app
    def quit_app(self):
        # closing capture
        if self.cap is not None:
            self.cap.release
    
        print('Quitting application...')
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # getting screen res
    width,height = app.primaryScreen().size().toTuple()

    window = MyApp()
    window.show()
    
    sys.exit(app.exec())
