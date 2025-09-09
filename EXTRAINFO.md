## How does it work?

### Structure

The **main thread in app.py** calls the <code>start_level</code> function in levels.py to start a level (still on main thread, just executing a func in levels), passing a level number as an argument and giving some premade empty self variables for it to return to. 

The levels.py <code>start_level</code> function makes a few custom Qt objects (declared in helper function) to start the basic level GUI while in the main thread. It also **makes the camera pose detection thread**. It then calls the <code>setup_level</code> function to make the needed objects specific to the selected level. There will be a different level_setup function for each level; it is written by the level designer to create any more QObjects unique for their level **while still in the main thread.** 

The start_level function finally **makes the level thread to run the <code>level_#</code> function**; The game logic thread is given access to the pointers for the camera/pose thread and all the created objects - it will be reading the calulations of the camera thread and causing changes in main using the **event invoker** <code>invoke</code> declared in helper. The event invoker allows calling object functions safely from outside the main thread (basically just adds the function call to the event queue for the main thread to execute, along with a small buffer to prevent overwhelming the main thread). See [the code used](https://stackoverflow.com/questions/10991991/pyside-easier-way-of-updating-gui-from-another-thread) for more information.

**The game logic thread runs the function corresponding to the level selected. Writing one of these functions is how one writes a level.**

Finally with those two threads running in the background, **we turn our attention back to the main thread,** currently blocking the GUI as it's still completing the levels.py function call. The levels.py function **returns the new GUI objects and the pointers to the two running threads** back to the awaiting main class. The GUI resumes being responsive with references to all objects and threads, allowing you to gracefully quit.

When the level is quit, a signal is sent for all the threads to gracefully exit and the QObjects holding the level UI and signals are destroyed.

<code> Thread communication visualization: </code>

        MAIN GUI ←——— GAME LOGIC ←——— CAM/POSE ML
            :
            |             ↑               ↑
            |_____________|_______________|
             only to tell them start/stop

This is all done using the python threading module, so the python GIL is still in place. 

<br>

###  Machine Learning Models 

This program uses machine learning to detect and classify the user's input. The actual machine learning models used in poseestim.py consist of MediaPipe's pose estimation model (to get the position of various body points) and a subsequent **[Random Forest](https://en.wikipedia.org/wiki/Random_forest)** model (to classify the exercise based on those points) made with Scikit Learn. MediaPipe's pose estimation architecture is based on **[BlazePose](http://arxiv.org/pdf/2006.10204)** and **[MobileNetV2](https://arxiv.org/pdf/1801.04381)**, which are both **[Convolutional Neural Networks](https://en.wikipedia.org/wiki/Convolutional_neural_network)**.

If you plan to create your own models to detect different kinds of poses as input, a helper file is included to capture pose data and a training file for creating a random forest classifier in scikit using that data. Remember to update the exercise detection function in the Pose_Estimation class to use your own model. I recommend sticking to a random forest classifier, as it's generally good "out of the box" when it comes to high dimensional data with few training examples, and inference calculation time is relatively fast compared to other multi-class classifiers. That being said, ML model performance depends on a ton of factors and can often be counterintuitive, so go wild and experiment.

### <u>ADDENDUM:</u>

It's important to acknowledge that while ML and AI are extremely useful tools, they are imperfect and prone to bias. Furthermore, many corporations have felt emboldened to scrape data from unconsenting netizens and artists to train their models. In addition to this being a violation of ethics, it also results in undocumented training datasets which cannot be easily checked for problems.

I have trained the random forest models myself, and since I am only one person with one body, there might be some overfitting. To mitigate this, I have provided some tools to make your own training data. As for the mediapipe pose estimation model, they do not explicitly say which dataset they use; However, as the scale of the dataset is small enough to where they have all been human labelled, it gives me hope that the researchers have taken the proper ethical considerations - both to mitigate bias and to respect the rights of the people in the training images. 

<br>

### Why go through all these hoops instead of just doing everything in app.py?

I organized everything to the best of my ability to make things easier for anybody who might want to build off of this in the future. My main goal was to keep levels.py as isolated as possible for people who just want to make some fun games, while also making the rest neat and legible for those who want to dig more into the wiring or change the GUI.

Ultimately this is meant to be a tool for building body tracking games, albeit a simple one.

<br>