# Contents

This folder contains an exercise detection random forest model and  three python files aimed to help create/train your own.

<code>data_gatherer.py</code> is a small app to help gather pose data. It excludes all points beyond the wrist and ankle, and also excludes the eyes and mouth. To change this, change the <code>ignore</code> variable in the <code>preprocess</code> function in <code>data_gatherer.py</code> (and also in <code>poseestim.py</code> if you're implementing the new model you create).

<code>randforest_creator.py</code> is a small script to combine the data into one and train a random forest model on it.

The third python file is <code>enumop2.py</code>, which just contains file paths to the models so you can change them there easily rather than dive into the code. Similar to <code>enumoptions.py</code> in source directory.

Finally, I'm aware Google's "Teachable Machine" has a similar use to this, but it can only train the model using transfer learning, losing the ability to just predict the body coordinates. It would also make switching between models (lite, full, heavy) extremely impractical.

# How to Use

## Step 1: Gather Data

Run <code>data_gatherer.py</code> using the python environment that has all the requirements downloaded (look up how to use python environments if you're new to python). This should bring up a GUI app which helps collect your own pose data using your camera. It writes this data to a file you specify. It appends data without erasing, so feel free to write to the file multiple times. The file must be a CSV file.

When collecting the data, you simply make the pose you want to be able to detect while the camera collects the data. This can be a specific pose, or a general cohesive category of poses that can all carry the same label. There is no line in the sand for what counts as a cohesive label, just like in human language. Don't be afraid to experiment, see what works for you.

**Important: The file should hold data corresponding to only one category you are trying to detect/classify.** 
When you want to collect data for a different category/label, switch to a different file. I recommend naming the files according to the category/label so you don't mix them up.

Once you have collected data for all the different poses you want to detect, it's time to make the model.

## Step 2: Create the Model 

We will use the data to train a simple statistical model called a random forest classifier. This is a whole bunch of decision trees (a decision tree is like a bunch of if-else statements), the results of which are then aggregated to give one output. The values the trees split on go through changes during training until they can accurately capture the relationship between body position data and the pose labels we assign to them. The input data is the pose data, and the output is a label or category.

![A visualization of a decision tree which predicts the probability of Kyphosis after spinal surgery.](https://upload.wikimedia.org/wikipedia/commons/2/25/Cart_tree_kyphosis.png)

^ An example of a decision tree which predicts the probability of Kyphosis after spinal surgery, by <a href="//commons.wikimedia.org/w/index.php?title=User:Stephen_Milborrow&amp;action=edit&amp;redlink=1" class="new" title="User:Stephen Milborrow (page does not exist)">Stephen Milborrow</a> - <a href="https://creativecommons.org/licenses/by-sa/4.0" title="Creative Commons Attribution-Share Alike 4.0">CC BY-SA 4.0</a>, <a href="https://commons.wikimedia.org/w/index.php?curid=68192267">Link</a>

Open up <code>randomforest_creator.py</code> in a text editor. We'll need to write a tiny bit of code. Don't worry if you're a beginner or not a programmer, comments are provided to guide you, although some basic python knowledge is recommended.

Under where it says <code># CSV File Locations</code> in line 16, you will find some variables (by default 3). These variables should correspond to the files you collected data in and need to hold their file paths. **Change the variables accordingly.** 

If you've placed your CSV files in this folder, you can change just the last argument and not deal with the file paths at all:

<code>YOUR_VAR_1 = os.path.join(enumop2.root_dir, 'models', 'exercise_model', 'YOUR_FILE_1.csv')</code>

or just make the variable a string containing the absolute file path, i.e:

<code>YOUR_VAR_2 = 'C:/Your/File/Path/Here/YOUR_FILE_2.csv'</code>

Once you have a variable for all your files, you just need to make some variables labels. The labels will correpsond to the files, and it will dictate what the model spits out as an output. I like for my models to spit out numbers because it makes comparisons easier, but it's easy to forget which number corresponds to what label.

The labels are where it says <code># Class Labels</code> (around line 25). **Write your own variables for the labels - there should be as many labels as there are files.** The variables will hold the output the model spits out at you. Here's an example using numbers:

<code>YOUR_LABEL_1 = 0</code>

Here's an example using text:

<code>YOUR_LABEL_2 = 'parry'</code>

Finally, under <code># Putting all the variables in a list to process</code> (around line 34), you just add the files to a file list and the labels to a label list. The order of the files and labels must correspond to each other, so the file with category A must be in the same spot in the file list as the label for category A is in the label list. 

Do not change the name of the list variables, just change the contents of the variable (the stuff after the equals sign). For example:

<code>files = [YOUR_FILE_1, YOUR_FILE_2]</code>

<code>class_labels = [YOUR_LABEL_1, YOUR_LABEL_2]</code>

Now you're done! Just run the file and the program will give you a model in the form of a .joblib file which you can use elsewhere in the code. It will also output the accuracy of the model in the console log.