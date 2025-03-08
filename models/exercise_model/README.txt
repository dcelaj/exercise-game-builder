This folder contains an exercise detection random forest model, 
three python files aimed to help create/train your own, and a yml.

data_gatherer.py is a small app to help gather pose data. It 
excludes all points beyond the wrist and ankle, and also excludes
the eyes and mouth. To change this, change the 'ignore' variable
in the 'preprocess' function in data_gatherer.py (and also in 
poseestim.py if you're implementing the new model you create).

randforest_creator.py is a small script to combine the data into
one and train a random forest model on it. This requires pandas.

The third python file is enumop2.py, just contains file paths to
the models so you can change them there easily rather than dive 
into the code. Similar to enumoptions.py in source directory.

Since I did this step on a different computer, I don't know if
installing pandas causes any problems - if it does, use the yml
file as a backup of the original conda env. Recreate it with:
conda env create -f conda_exercise_environment.yml
EDIT: I've tested the whole thing with pandas again and it works 
but I'll leave the yml file just in case.

Finally, I'm aware Google's teachable machine has a similar use
to this, but it can only train the model using transfer learning,
losing the ability to just predict the body coordinates. It would
also make switching between models (lite, full, heavy) impractical
if not impossible. 