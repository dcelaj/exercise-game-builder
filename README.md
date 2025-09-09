# Exercise Game Builder

This is a small exercise game builder programmed in Python. The program uses the computer's camera and tries to detect a user's pose, instructing them to complete exercises to progress and responding to the user's exercise. I use **PySide6/Qt** for the GUI, **MediaPipe** and **OpenCV** to achieve the pose estimation, **Pandas, Numpy, and Scikit Learn** for some extra machine learning tools, and **PyInstaller** to package everything.

I've structured the project so that it's simple for others to modify it and add levels. If you see this out in the wild, **feel free to use any of this code** to make a proper game (just abide by the licensing rules of the packages used); the main pose estimation code doesn't use any Qt in it at all, so you can just lift that if you want to use a completely different GUI and game structure. 

As it stands this is mainly a personal project to integrate GUIs, multithreading, and machine learning into one project - I'm certainly not a good enough artist to turn this into a proper game myself.

## Requirements

**Python 3.11 or later** is recommended, just make sure that the version can install all the packages in requirements.txt properly. **You'll also have to download the mediapipe models yourself** [here](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) and put them in the mediapipe folder.

## Project Structure

The project file structure is as follows:

- The **assets** folder contains the game art and sound, along with a few other misc items. The art is mainly png files, but I'm considering support for 3D assets. Right now there are two NPCs and two backgrounds hastily put together for testing and demo. Feel free to delete anything here and replace with your own assets (except for blank.png, since that's used as a default case).
- The **models** folder contains the machine learning models used in the game.
    - **You'll have to download the mediapipe models yourself** [here](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) and put them in the mediapipe folder.
    - The exercise detection model I've created is included with some helper files to create your own model - more info below.
- The **saves** folder is used to collect any file outputs - put your settings or save files here if you wish.
- The **source** folder contains all the python code and modules.
- The **requirements** text file contains all the packages needed to run this code.
- The exact versions of everything I used in development are given in the **version-info** text file.
- The **GUIDE** markdown file goes into more detail on how to make a level, and the **EXTRAINFO** one goes into more detail on how the program works in general.

The source folder contains:

- **app.py**, the main file, it includes GUI elements, event loop, and calls functions from the levels file to start an exercise set.
    - You probably want to make your own custom GUI; the only things you really have to preserve are **level_button_clicked**, **close_level**, the **Level_Widget**, and the imports.
- **levels.py**, this file contains all the game's levels. It references the poseestim and helpers files to construct the actual gameplay in a level.
    - To make a level, you'll want to write the functions for the game logic... 
        - One **setup** func for instantiating - from the main thread - the objects needed in your level,
        - and a **level** func for the actual game logic and events to run in that new level thread.
    - ...and slightly edit the **starter** function by adding the case for your level.
- **poseestim.py**, this file contains all the code for taking camera input and feeding it to the machine learning models for pose estimation and classification.
    - You'd be altering this if you wanted to add a new type of classifier/exercise.
- **helpers.py**, this file contains the code for the other aspects of the game, mainly the animations and game UI.
    - It also contains the **event invoker function**, which is needed for the different threads to safely interact with the Qt GUI. If you want to use a different GUI library, you'll want to find a replacement for this.
- **enumoptions.py** contains some enums for more readable options and also file path stuff. If you make your own model, add the path.

## Credits

In addition to all the packages, software, hardware, and overall technology which made this project possible, I'd like to credit some material which I used as reference along the way - particularly [PythonGUIs.com's PySide 6 tutorials](https://www.pythonguis.com/pyside6-tutorial/). I also referenced github user [bsdnoobz's code](https://gist.github.com/bsdnoobz/8464000) on reading a camera feed with PySide, [Boris Runa's post](https://forum.qt.io/topic/132670/capture-opencv-video-and-present-it-on-qvideowidget) on the Qt forums on doing the same with PyQt, and [Armatita's stackoverflow answer](https://stackoverflow.com/questions/44264852/pyside-pyqt-overlay-widget) to make the transparent overlay in PySide. Finally, [chfoo and Petter's stackoverflow answers](https://stackoverflow.com/questions/10991991/pyside-easier-way-of-updating-gui-from-another-thread) on safely posting events to the main thread were a godsend.

While I didn't directly reference any code from these, [William Sokol's head tracking project](https://github.com/williamsokol/HeadTrackingInGodotHTML5) sparked the initial project idea, and [Nicholas Renotte has a similar MediaPipe project](https://github.com/nicknochnack/MediaPipePoseEstimation) to my program (although his code is outdated for the current mediapipe version, his video had some pretty valuble insight that MediaPipe's documentation lacks).

The demo assets were all made by me, mostly hand drawn with some nearly decade old acrylic paints I had from an old art class. One was done in [Blender](https://www.blender.org/). All images were digitally edited in [Krita](https://krita.org/en/). Highly recommend both programs, very fun to mess around in, and they're free so you've nothing to lose.

</br>
<hr>
</br>

### Possible improvements / TODO

- [ ] Look into using skl2onnx over joblib for [security](https://security.snyk.io/vuln/SNYK-PYTHON-JOBLIB-3027033) - **high priority**
- [x] Look into why performance slows when no person in frame - see if MP has early abort option **(fixed)**
- [x] Test to see if an ack feedback mechanism in <code>invoke()</code> would work better than buffering events with <code>sleep()</code>  *(buffering seems to be faster, but the feedback mechanism I built wasn't optimal - don't discard this idea yet)*
- [x] Make full exercise classifier to replace placeholder mini one & finish demo level *(done!)*
- [x] Write guide on how to use
- [ ] Make custom image annotation function in helpers
- [ ] Add in support for config file to store preferences (console log, model used, player name, etc...)
- [ ] Add a tester python file that mimics the cam/pose output with dummy data so user doesn't have to wait 5-6 seconds every time to test a level
- [ ] ~~Look into possibly supporting 3D assets - would need a different library to handle 3D assets and print out camera view to pixmap.~~ 
    - *Would probably be more efficient to write an API integrating MP into an existing game engine though. Possible future project.*
