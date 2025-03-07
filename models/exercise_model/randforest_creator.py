import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
import enumop2 
import os

''' 
This python file uses scikit learn to make a random forest classifier based on all the pose data. It combines the data
into a single DataFrame object and uses that to train the model.
'''
#
'''THESE ARE THE VARIABLES YOU WANT TO CHANGE'''

# CSV File Locations
csv0 = os.path.join(enumop2.root_dir, 'models', 'exercise_model', 'c0.csv')
csv1 = 'path'
csv2 = 'path'
# This code looks in exercise_model folder for files named 'c0.csv' 'c1.csv' 'c2.csv' - if your files are in this folder,
# all you have to do is replace the last argument with the name of your file. You can also just paste in the absolute file 
# path as a string.

# Class Labels
DEFAULT = 0
STATE_A = 1
STATE_B = 2
# I personally put my data for a default/rest state in csv0, the data for the eccentric phase of the exercise in csv1, and 
# the data for the concentric phase in csv2 - this ended up weirdly successful for classifying a bunch of exercises.
# If you're a beginner and confused by this, look up class labels in machine learning - lots of good resources online.

# Feature Labels
# x, y, z are spatial coords, v is visibility, and the number shows which body landmark they belong to
features = ['x0', 'y0', 'z0', 'v0',
            'x1', 'y1', 'z1', 'v1',
            'x2', 'y2', 'z2', 'v2',
            'x3', 'y3', 'z3', 'v3',
            'x4', 'y4', 'z4', 'v4',
            'x5', 'y5', 'z5', 'v5',
            'x6', 'y6', 'z6', 'v6',
            'x7', 'y7', 'z7', 'v7',
            'x8', 'y8', 'z8', 'v8',
            'x9', 'y9', 'z9', 'v9',
            'x10', 'y10', 'z10', 'v10',
            'x11', 'y11', 'z11', 'v11',
            'x12', 'y12', 'z12', 'v12',
            'x13', 'y13', 'z13', 'v13',
            'x14', 'y14', 'z14', 'v14',]
# My lack of foresight caused me to forget pandas has column labels so I'm just manually adding them in here.

# Putting all the variables in a list to process
files = [csv0, csv1, csv2]
class_labels = [DEFAULT, STATE_A, STATE_B]
#
#
# Below is the data processing and scikit learn code
#
#

# Function combining the files to be used by sklearn
def load_and_concatenate_data(file_paths:list, labels:list, col_names:list):
    """
    Load data from multiple files and concatenate them into a single DataFrame with an added 'class' column.
    """
    # Initialize an empty list to store DataFrames
    data_frames = []
    
    # Loop over file paths and labels to load and label data
    for file_path, label in zip(file_paths, labels):
        # Read the purely numeric csv
        df = pd.read_csv(file_path, header=None)

        # Add the feature/column names
        df.columns = col_names

        # Add a class column
        df['class'] = label

        # Append to the list of DFs
        data_frames.append(df)
    
    # Concatenate all DataFrames
    data = pd.concat(data_frames)
    return data

# Making DataFrame
data = load_and_concatenate_data(files, class_labels, features)
# Putting all pose data in one var and all the corresponding classes in another
pose_data = data.drop('class', axis=1)
pose_class = data['class']
# Further split into training and testing data sets
pose_data_train, pose_data_test, pose_class_train, pose_class_test = train_test_split(pose_data, pose_class, 
                                                                                      test_size= 0.15, random_state= 1)


# Initialize and train the Random Forest model
rf_model = RandomForestClassifier()
rf_model.fit(pose_data_train, pose_class_train)

# Evaluate the model
accuracy = rf_model.score(pose_data_test, pose_class_test)
print(data)
print(f"Accuracy: {accuracy}")

# Save the dummy model using joblib
joblib.dump(rf_model, 'randomforest_model.joblib')

print("Random Forest model created and saved successfully!")
