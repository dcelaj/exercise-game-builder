'''
This uses scikit learn to make a random forest classifier based on all the pose data.
The model, once finished training, will be exported using joblib (or ONNX but that's
for later optimization.)

I considered using google's tensorflow (or the new dedicated decision tree library),
but since I couldn't find any resources on whether they were supported by tensorflow
Lite (the format media pipe uses), I figured it would end up in a different format
anyway, and more people know sklearn.

I've added it to a global helper func, so if you wanna change over to tensor flow,
just edit the exercise detection helper func in poseestim and leave the class alone.
'''