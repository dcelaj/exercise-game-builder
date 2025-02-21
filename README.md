# Exercise Test Game

This is a small exercise game programmed in Python. The program uses the computer's camera and tries to detect a user's pose, instructing them to complete exercises to progress and responding to the user's exercise. I use **PySide6** and **Qt** for the GUI and event loop, the open source **MediaPipe** project (which itself uses absl-py, attrs, flatbuffers, jax/jaxlib, matplotlib, numpy, opencv, protobuf, sounddevice, sentencepiece) to achieve the pose estimation, and **PyInstaller** to package everything.

I've structured the project so that it's simple for others to modify it and add levels. If you see this out in the wild, feel free to use any of this code to make a proper game (just abide by the licensing rules of the packages used). As it stands this is mainly a personal project to integrate GUIs, multithreading, and machine learning into one project - I'm certainly not a good enough artist to turn this into a proper game myself. 

Eventually I hope to make a C library to port MediaPipe into a proper game engine like Godot, but for now this serves as a solid first step.

## Project Structure

The project file structure is as follows:

- The **assets** folder contains the game art and sound, along with a few other misc items.
- The **models** folder contains the machine learning models used in the game.
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
    - The asyncestim.py file is a WIP
- **helpers.py**, this file contains the code for the other aspects of the game, mainly the animations and dialogue. You might be adding some stuff here too if you wanna make custom animations.

## Credits

In addition to all the packages and technologies which made this project possible, I'd like to credit some material which I used as reference along the way - particularly [PythonGUIs.com's PySide 6 tutorials](https://www.pythonguis.com/pyside6-tutorial/). I also referenced github user [bsdnoobz's code](https://gist.github.com/bsdnoobz/8464000) on reading a camera feed with PySide and [Boris Runa's post](https://forum.qt.io/topic/132670/capture-opencv-video-and-present-it-on-qvideowidget) on the Qt forums on doing the same with PyQt.

Finally, while I didn't directly reference any code from these, [William Sokol's head tracking project](https://github.com/williamsokol/HeadTrackingInGodotHTML5) sparked the initial project idea, and [Nicholas Renotte has a similar MediaPipe project](https://github.com/nicknochnack/MediaPipePoseEstimation) to my program (although his code is outdated for the current mediapipe version).

</br>
<hr>
</br>

## How does it work?

The **main thread in app.py** calls the startup function in levels.py to start a level (still on main thread rn, just executing a func in levels), passing a level number as an argument and giving some premade empty self variables for it to return to. 

The levels.py function makes custom GUI Qt objects (declared in helper function) to start the level GUI, and also makes some signal handler objects to connect to the custom GUI. It connects the signal handlers to some basic lambda functions to keep the main app.py file clean. (Still in main thread, just creating new objects and handlers to give to Main Window class)

The levels.py function finally **makes two new threads**: the camera/pose estimation thread and the game logic thread, in that order. The game logic thread is given access to the pointers for the camera/pose thread and all the handler objects - it will be reading the calulations of the camera/pose thread and causing changes in main using the signal handler objects we gave it. 

**The game logic thread runs the function corresponding to the level selected. Writing one of these functions is how one writes a level.**

Finally with those two threads running in the background, **we turn our attention back to the main thread,** currently blocking the GUI as it's still completing the levels.py function call. The levels.py function **returns the new GUI objects, new signal handlers, and the pointers to the two running threads** back to the awaiting main class. The GUI resumes being responsive, allowing you to gracefully quit the threads and program.

When the level is quit, a signal is sent for all the threads to gracefully exit and the QObjects holding the level UI and signals are destroyed.

<code> Thread communication visualization: </code>

        MAIN GUI ←——→ GAME LOGIC ←——— CAM/POSE ML
            |                             ↑
            |_____________________________|
                (quit signal only)


### Why go through all these hoops instead of just doing everything in app.py?

I organized everything to the best of my ability to make things easier for anybody who might want to build off of this in the future. My main goal was to keep levels.py as isolated as possible for people who just want to make some fun games, while also making the rest neat and legible for those who want to dig more into the wiring or change the GUI.

Ultimately this is meant to be a tool for building body tracking games, albeit a simple one.