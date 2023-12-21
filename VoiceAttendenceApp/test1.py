from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
import re
import numpy as np
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os
import os
import librosa
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential
import subprocess

X_train = []
Y_train = []

def resize(a):
    width = 19200
    b = np.zeros(width)
    for i in range(len(a)):
        if len(a) < width:
            b[i] = a[i]
    return b

for root, dirs, directory in os.walk("F:\VR_attendance\Users"):
    for j in range(len(directory)):
        name = os.path.basename(root)
        #res = subprocess.check_output('ffmpeg.exe -i '+root+"/"+directory[j]+" "+root+"/1"+directory[j], shell=True)
        x, sr = librosa.load(root+"/"+directory[j], res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(x, sr=sr)
        mfccs = mfccs.ravel()
        temp = resize(mfccs)
        temp = np.reshape(temp,(80,80,3))
        X_train.append(temp)
        Y_train.append(int(name))
        
X_train = np.asarray(X_train)
Y_train = np.asarray(Y_train)
print(Y_train)
X_train = X_train.astype('float32')
indices = np.arange(X_train.shape[0])
np.random.shuffle(indices)
X_train = X_train[indices]
Y_train = Y_train[indices]
Y_train = to_categorical(Y_train)
print(X_train.shape)
print(X_train)
classifier = Sequential()
classifier.add(Convolution2D(32, 3, 3, input_shape = (80, 80, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2)))
classifier.add(Convolution2D(32, 3, 3, activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2)))
classifier.add(Flatten())
classifier.add(Dense(output_dim = 256, activation = 'relu'))
classifier.add(Dense(output_dim = Y_train.shape[1], activation = 'softmax'))
print(classifier.summary())
classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
classifier.fit(X_train, Y_train, batch_size=16, epochs=10, shuffle=True, verbose=2)





