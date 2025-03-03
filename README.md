# Exercise Game Builder

This is a small exercise game programmed in Python. The program uses the computer's camera and tries to detect a user's pose, instructing them to complete exercises to progress and responding to the user's exercise. I use **PySide6**/**Qt** for the GUI, **MediaPipe** and **OpenCV** to achieve the pose estimation, **Numpy** and **Scikit Learn** for some extra machine learning tools, and **PyInstaller** to package everything.

I've structured the project so that it's simple for others to modify it and add levels. If you see this out in the wild, feel free to use any of this code to make a proper game (just abide by the licensing rules of the packages used). As it stands this is mainly a personal project to integrate GUIs, multithreading, and machine learning into one project - I'm certainly not a good enough artist to turn this into a proper game myself. 

Eventually I hope to make a C library to port MediaPipe into a proper game engine like Godot, but for now this serves as a solid first step.

## Project Structure

The project file structure is as follows:

- The **assets** folder contains the game art and sound, along with a few other misc items. The art is mainly png files, but I'm considering support for 3D assets.
- The **models** folder contains the machine learning models used in the game.
    - You'll have to download the mediapipe model with the link in the text file provided.
    - The exercise detection model I've created is included, along with some helper files I used to make the exercise detector if you want to train your own - more info is in the file comments.
- The **output** folder is used to collect any file outputs, mainly for debugging or final packaging.
- The **source folder** contains all the python code and modules.
- The plan png file is a **REALLY** rough sketch of how everything was set up and planned.
- The requirements text file contains all the packages needed to run this code - I recommend using a python version manager and setting up an environment for this. 
    - If you use Anaconda/Miniconda as I do, make sure you create an env with python explicitly installed (conda create -n "myenv" python) - otherwise using "pip" will just install the packages to your default python directory rather than the contained environment.

The source folder contains:

- **app.py**, the main file, it includes GUI elements, event loop, and calls functions from the levels file to start an exercise set. You'd only need to edit in buttons here if you plan to use this youself.
- **levels.py**, this file contains the levels and is the file you'll probably be adding to most heavily if you're using this for a custom game. It references the poseestim and helpers files to construct the actual gameplay in a level.
    - To make a level, you'll want to write the function for the game logic, and slightly edit the starter function (designed to be called from the main GUI and start both the pose estimation thread and the thread for the aforementioned game logic). 
    - The game logic thread will access info from the pose estim thread and use helper functions to react to what the player does - really sending messages to the main GUI thread to show the visuals reacting to the player's actions.
- **poseestim.py**, this file contains all the code for the camera and machine learning libraries for pose estimation - it uses mediapipe for the pose and feeds those numbers into other models depending on the exercise being done.
    - You'd only be altering this if you wanted to add a new type of exercise to detect - not suggested for beginners.
- **helpers.py**, this file contains the code for the other aspects of the game, mainly the animations and dialogue. You might be adding some stuff here too if you wanna make custom animations.

## Credits

In addition to all the packages and technologies which made this project possible, I'd like to credit some material which I used as reference along the way - particularly [PythonGUIs.com's PySide 6 tutorials](https://www.pythonguis.com/pyside6-tutorial/). I also referenced github user [bsdnoobz's code](https://gist.github.com/bsdnoobz/8464000) on reading a camera feed with PySide and [Boris Runa's post](https://forum.qt.io/topic/132670/capture-opencv-video-and-present-it-on-qvideowidget) on the Qt forums on doing the same with PyQt.

Finally, while I didn't directly reference any code from these, [William Sokol's head tracking project](https://github.com/williamsokol/HeadTrackingInGodotHTML5) sparked the initial project idea, and [Nicholas Renotte has a similar MediaPipe project](https://github.com/nicknochnack/MediaPipePoseEstimation) to my program (although his code is outdated for the current mediapipe version).

</br>
<hr>
</br>

## How does it work?

### Structure

The **main thread in app.py** calls the startup function in levels.py to start a level (still on main thread rn, just executing a func in levels), passing a level number as an argument and giving some premade empty self variables for it to return to. 

The levels.py function makes custom GUI Qt objects (declared in helper function) to start the level GUI, and also makes some signal handler objects to connect to the custom GUI. It connects the signal handlers to some basic lambda functions to keep the main app.py file clean. (Still in main thread, just creating new objects and handlers to give to Main Window class)

The levels.py function finally **makes two new threads**: the camera/pose estimation thread and the game logic thread, in that order. The game logic thread is given access to the pointers for the camera/pose thread and all the handler objects - it will be reading the calulations of the camera/pose thread and causing changes in main using the signal handler objects we gave it. 

**The game logic thread runs the function corresponding to the level selected. Writing one of these functions is how one writes a level.**

Finally with those two threads running in the background, **we turn our attention back to the main thread,** currently blocking the GUI as it's still completing the levels.py function call. The levels.py function **returns the new GUI objects, new signal handlers, and the pointers to the two running threads** back to the awaiting main class. The GUI resumes being responsive, allowing you to gracefully quit the threads and program.

When the level is quit, a signal is sent for all the threads to gracefully exit and the QObjects holding the level UI and signals are destroyed.

<code> Thread communication visualization: </code>

        MAIN GUI ←——— GAME LOGIC ←——— CAM/POSE ML
            :
            |             ↑               ↑
            |_____________|_______________|
             only to tell them start/stop

<br>

###  Machine Learning Models 

This program uses machine learning to detect and classify the user's input. The actual machine learning models used in poseestim.py consist of MediaPipe's pose estimation model (to get the position of various body points) and a subsequent **[Random Forest](https://en.wikipedia.org/wiki/Random_forest)** model (to classify the exercise based on those points) made with Scikit Learn. MediaPipe's pose estimation architecture is based on **[BlazePose](http://arxiv.org/pdf/2006.10204)** and **[MobileNetV2](https://arxiv.org/pdf/1801.04381)**, which are both **[Convolutional Neural Networks](https://en.wikipedia.org/wiki/Convolutional_neural_network)**.

If you plan to create your own models to detect different kinds of poses as input, a helper file is included to capture pose data and a training file for creating a random forest classifier in scikit using that data. You can use a different model - just update the exercise detection function in the Pose_Estimation class to use your own model (make sure to import the proper libraries if you aren't using scikit learn). I personally recomment sticking to a random forest classifier, as it's generally good "out of the box" when it comes to high dimensional data with few training examples, and inference calculation time is relatively fast compared to other multi-class classifiers. That being said, ML model performance depends on a ton of factors and can often be counterintuitive - if you build a model that works particularly well, please feel free to share it!

**Addendum:** It's important to acknowledge that while ML and AI are extremely useful tools, they are imperfect and prone to bias. Furthermore, many corporations have felt emboldened to scrape data from unconsenting netizens to train their models. In addition to this being a violation of privacy, it also results in undocumented training datasets which cannot be easily checked for bias. 

I have trained the random forest models myself, and since I am only one person with one body, there might be some overfitting. As for the mediapipe pose estimation model, they do not explicitly say which dataset they use. However, as the scale of the dataset is small enough to where they have all been human labelled, I would hope the researchers have taken the proper ethical considerations.

<br>

### Why go through all these hoops instead of just doing everything in app.py?

I organized everything to the best of my ability to make things easier for anybody who might want to build off of this in the future. My main goal was to keep levels.py as isolated as possible for people who just want to make some fun games, while also making the rest neat and legible for those who want to dig more into the wiring or change the GUI.

Ultimately this is meant to be a tool for building body tracking games, albeit a simple one.

<br>

### Possible improvements / TODO

- [x] Consider moving MediaPipe's image annotation to helpers.py to spread the loads between threads more evenly
    - I think I'm **not** going to do this, because it would be messier and harder to use
    - Performance increase also not likely too significant - may be worth some tests though
- [x] Look into whether MediaPipe task resizes image internally before processing. If not, downsizing beforehand could improve performance.
    - I can't image this isn't being done, since accepting different resolutions would complicate the neural net heavily. But worth checking.
    - Haven't been able to find concrete confirmation, but I'm 99% sure it resizes internally, so **no action** will be taken.
- [ ] Look into using skl2onnx over joblib for better security and optimization