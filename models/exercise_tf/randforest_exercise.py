'''
This uses scikit learn to make a random forest classifier based on all the pose data.
The model, once finished training, will be exported using joblib (or ONNX but that's
for later optimization.)

rn just makes some dummy data for testing
'''

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Create dummy data
X_dummy = np.random.rand(1000, 33) # 1000 random dummy points, each having 33 features/dimensions
y_dummy = np.random.randint(3, size=1000) # 3 cateogries

# Initialize and train the Random Forest model
dummy_rf_model = RandomForestClassifier()
dummy_rf_model.fit(X_dummy, y_dummy)

# Save the dummy model using joblib
joblib.dump(dummy_rf_model, 'dummy_big_rf_model.joblib')

print("Dummy Random Forest model created and saved successfully!")
