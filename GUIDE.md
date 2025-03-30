# Guide

A simple guide on making a game using this project. This will contain a lot of the same info in the readme but presented in a way that's easier to follow. **Please keep in mind this guide assumes some basic python knowledge,** but should be a decent jumping off point for beginners.

## Before Getting Started

This whole thing is a project made by one person, and as such it will have flaws. I probably wouldn't use it to make a product you're going to sell, not without extensive changes anyway.

Finally, this project uses PySide6, a python wrapper for Qt. Qt does have a proper application where you can put things together visually without writing the code, and there are plenty of nice looking Qt GUIs others have made available for free, but either way it's tricky to use. That's something you want to consider before starting a large project using this as the base.

If you want the end result to be super polished, you should look up some pre-built PySide6 Qt GUI assets and familiarize yourself with the basics of Qt - just enough to implement those pre-written assets. It might be a couple hours of frustration, but it's definitely possible to get something nice looking even as a beginner.

## Setup

Using your preferred python version manager, make a new environment and install the requirements. The **requirements** text file contains all the packages needed to run this code. **Python 3.11 is recommended**, anything after 3.11 that can still install the requirements should also work.

- If you use Anaconda/Miniconda as I do, make sure you create an environment with python explicitly installed (conda create -n "myenv" python=3.11) - otherwise using "pip" will just install the packages to your default python directory rather than the contained environment.

Finally, download the mediapipe models yourself [here](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) and put them in the mediapipe folder. I recommend downloading all three, as they're all good for different cases (prioritizing responsiveness vs accuracy).

Now try running the app.py python file and playing level 0 - if level 0 succesfully starts detecting your pose, you're all set to start making your own level!

## Editing <code>app.py</code>

The main GUI is handled in <code>app.py</code>. This is the file you have to run to start your game application.

You probably want to make your own custom GUI that isn't so bare bones; the only functions you really have to preserve are **level_button_clicked** and **close_level**, since those set up the play area, recieve the thread pointers, and gracefully terminate them. And the imports, those are important too.

The file contains comments documenting what code is respondible for what page of the app - a simple way to get started customizing is [adding some CSS to the Qt Widgets](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/widgetstyling.html) and [play around with their layout](https://www.pythonguis.com/tutorials/pyside6-layouts/). Maybe add some labels to serve as titles for each menu page.

Qt is a deep rabbithole with plenty of other tools. I find starting with CSS and basic widgets to be a *lot* less overwhelming while still being able to achieve some fancy results.

## Editing <code>levels.py</code>

This is where the actual level code resides. This is the file you'll probably be adding to most heavily if you're using this for a custom game. 

To make a level, you'll want to write the functions for the game logic... 

- One **setup** function for instantiating - from the main thread - the objects needed in your level,
- and a **level** function for the actual game logic and events to run in that new level thread.

...and slightly edit the **starter** function (which <code>app.py</code> calls when you press a level button) by adding the case for your level.

The game logic thread will access info from the camera thread and use helper functions to react to what the player does (both by changing internal variables and the graphics shown on screen).

### Setup Function

The reason we need a setup function is that our game assets are objects which cannot be safely created outside of the main thread. The setup function is executed while still in the main thread, so we create the objects there and then pass them along to our other threads.

I've written a couple of custom Qt objects for use in the game:

- <code>Q_NPC</code>, a Qt Object that holds an NPC. Takes as arguments the name of the NPC, a list of paths to the sprites of said NPC, and the relative position.
    - Functions include all of the functions a normal QGraphicsObject has, in addition to:
        - <code>set_new_img</code>
        - <code>cycle_img</code>
        - <code>set_norm_pos</code>
- <code>Overlay</code>, a QWidget which acts as the game overlay containing the dialogue text, NPC portrait, and player portrait and stats.
    - Functions include all of the functions a normal QWidget has, in addition to:
        - <code>pp.update_frame</code>
        - <code>pp.update_stat_bar</code>
        - <code>np.set_new_img</code>
        - <code>np.set_new_img_list</code>
        - <code>np.cycle_img</code>
        - <code>np.set_new_name</code>
        - <code>set_text</code>

You can use these as normal in the setup, since you're still in the main thread. Don't forget to add the items to the scene. Here you can read up a little more on [QGraphicsScene](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QGraphicsScene.html) and [QGraphicsView](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QGraphicsView.html).

As of now all the game assets are represented by Qt Objects. If you have some technical know-how, however, it's definitely not impossible to implement your own system for handling assets.

### Level Function/Thread

This is where the actual game loop and logic takes place. You are in charge of doing all the checks for player input, the NPC and UI response to those inputs, and the various conditions that win or lose the game.

This is all up to you.

#### It is important to note that the functions of the Qt Objects described above **should not be called normally while in this thread**, as Qt Objects are not thread safe. You should **instead use <code>invoke(object.function, arguments)</code>**, a piece of code which tells the main thread to execute the object function when it has time.

Don't use <code>invoke_in_main_thread</code>, that's only used internally in the <code>invoke</code> function.

### Camera Thread

This thread reads your camera input and passes it through two machine learning models - one being MediaPipe's pose estimation model to output estimated coordinates of body parts, and the second being a random forest classifier to take that output and classify it. You don't really need to worry about this thread (unless you want to change the type of classifier), you just need to know how you can read its output. 

If you DO want to know more about how these models work, read the "Machine Learning" and "ADDENDUM" sections in the README.md file.

Anyways, to read from this thread, use:

- <code>get_default_annotation</code>, returns an image (ndarray) depicting the detected body part positions, looks kinda like a stick figure
    - Two **optional** boolean arguments, hide_cam (draws the results on a black bg instead of on the camera image), and safe (makes it thread safe)
- <code>get_results</code>, returns all the results (camera input image, mediapipe results, exercise detection results, mask) in a thread safe manner
- <code>set_exercise</code>, changes the exercise classification model safely (only change the exercise variable with this function)
    - **Takes one argument**, an integer corresponding to the exercise or movement you want to detect
        - What numbers correspond to what exercises is in the <code>enumoptions.py</code> file
- <code>get_body_part</code>, returns the coordinate position and visibility of a given body part (easier than decoding the raw model output)
    - **Takes one argument**, corresponding to the body part you want the position of. See the below image for a helpful guide.

<details>
<summary> Click here to reveal the image guide. </summary>

![MediaPipe Body Pose Guide](https://ai.google.dev/static/edge/mediapipe/images/solutions/pose_landmarks_index.png) 

</details>

<br>

Feel free to read the read-only public variables at any time. While technically not thread safe, the way this was written combined with Python's Global Interpreter Lock means the worst that will happen is your reading will be slightly outdated by a few milliseconds. These are the most useful ones:

- frame, the image the camera currently sees (ndarray)
- exercise, the integer alias of the current exercise being detected (see <code>enumoptions.py</code> to see what numbers correspond to what exercise)
- ex_results, the results of the exercise classifier model (a deque with length of 32, about 2 seconds worth of detections)

Side note, if you're new to programming, this is an awful attitude to take with thread safety. 
<details>
<summary>Here are all the reasons why my statements above are stupid and oversimplified:</summary>

It's technically wrong to say a crash couldn't happen here. For one, numpy is involved which uses C to do its black magic and in the process releases the Global Interpreter Lock. But even if everything was 100% vanilla python with the GIL active, python bytecode doesn't only consist of atomic operations.

It's easy to forget the nightmarish complexity of the underlying hardware and operating system. The python you write is parsed and becomes an abstract syntax tree, which is then compiled into python bytecode. Then, of course, the python bytecode is handled by the Python Virtual Machine (normally written in C), the resulting machine code is given to the operating system, and ten million steps later becomes the electrical signals in your computer chip (those ten million previous steps were also electrical signals on the chip, just these ones now actually correspond to the instructions you coded - a portion of them at least).

As a programmer you are given a neat and tidy abstraction to work with, so it's best practice to play by the rules of that abstraction unless you're sure that none of those 10 million hidden variables will ruin your day (of course there are also plenty of times when breaking these rules is necessary, and plenty of people with the insane experience and knowledge to pull it off).

THAT BEING SAID, I take this attitude here is because this is a stupid game that is available for free. The resulting implementation is safe enough, faster, and easier to write. If a crash happens, I get to have fun trying to piece together what exactly happened on the instruction level. Experimenting and breaking stuff is fun, live a little, use some non thread safe code as a treat.
</details>
<br>
TL;DR: If you decide to make a product for sale using this, I'd stick to using the thread safe <code>get_results</code>.

<br>

And of course, **feel free to reference or copy from the code in the demo level** if you find you're having trouble. I may have gone a bit overkill on the comments, but I wanted this to be accessible to beginners.

## I want to detect different movements/poses as input - How do I do that?

All you have to do is create your own random forest model - see the <code>GUIDE.md</code> in the <code>/models/exercise_model</code> folder for step by step instructions on that. Again, only some basic python knowledge is needed.