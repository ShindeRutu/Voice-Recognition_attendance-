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
from datetime import date

global filename
global count
global X_train, Y_train
global classifier

def resize(a):
    width = 19200
    b = np.zeros(width)
    for i in range(len(a)):
        if len(a) < width:
            b[i] = a[i]
    return b

def train():
    global classifier
    global X_train, Y_train
    X_train = []
    Y_train = []
    for root, dirs, directory in os.walk("Users"):
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

def getUser(userid):
    name = 'unable to predict'
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select username FROM register where user_id='"+userid+"'")
        rows = cur.fetchall()
        for row in rows:
            name = row[0]
            break
    return name        

def markAttendence(name):
    today = date.today()
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
    index = 0
    output = "none"
    with con:
        cur = con.cursor()
        cur.execute("select username FROM attendence where username='"+name+"' and attended_date='"+str(today)+"'")
        rows = cur.fetchall()
        for row in rows:
            index = 1
    if index == 0:
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO attendence(username,attended_date) VALUES('"+name+"','"+str(today)+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        output = "Attendence successfully marked for user: "+name+" on date: "+str(today)
    else:
        output = name+" attendence already marked"
    return output    
        

@csrf_exempt
def attendence(request):
    if request.method == "POST":
        if os.path.exists('test.wav') == True:
            os.remove('test.wav')
        if os.path.exists('test1.wav') == True:
            os.remove('test1.wav')
        audio_data = request.FILES.get('data')
        fs = FileSystemStorage()
        fs.save('test.wav', audio_data)
        res = subprocess.check_output('ffmpeg.exe -i '+'test.wav'+" "+'test1.wav', shell=True)
        x, sr = librosa.load('test1.wav', res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(x, sr=sr)
        mfccs = mfccs.ravel()
        temp = resize(mfccs)
        temp = np.reshape(temp,(80,80,3))
        testData = []
        testData.append(temp)
        testData = np.asarray(testData)
        train()
        predict = classifier.predict(testData)
        predict = np.argmax(predict)
        print(predict)
        name = getUser(str(predict))
        print(str(predict)+" "+name)
        output = markAttendence(name)
        return HttpResponse("User recognized as "+name+"\n"+output+"\n\n", content_type="text/plain")

def User(request):
    if request.method == 'GET':
       return render(request, 'User.html', {})

def TrainModel(request):
    if request.method == 'GET':
        train()
        context= {'data':'Training process completed'}
        return render(request, 'AdminScreen.html', context)

def ViewAttendence(request):
    if request.method == 'GET':
        output = ''
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM attendence")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="" color="white">'+row[0]+'</td><td><font size="" color="white">'+str(row[1])+"</td></tr>"        
        context= {'data':output}
        return render(request, 'ViewAttendence.html', context)
        

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})

def Logout(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def successrecording(request):
    if request.method == 'GET':
        data = request.GET.get('t1', False)
        context= {'data':data}
        return render(request, 'Register.html', context)

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'Admin.html', context)
    

def UserLogin(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      index = 0
      con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
      with con:    
          cur = con.cursor()
          cur.execute("select * FROM register")
          rows = cur.fetchall()
          for row in rows: 
             if row[0] == username and password == row[1]:
                index = 1
                break		
      if index == 1:
       context= {'data':'welcome '+username}
       return render(request, 'UserScreen.html', context)
      else:
       context= {'data':'login failed'}
       return render(request, 'User.html', context)

@csrf_exempt
def SignupRecord(request):
    global count
    if request.method == "POST":
        audio_data = request.FILES.get('data')
        fs = FileSystemStorage()
        fs.save('Users/'+str(count)+'/1.wav', audio_data)
        fs.save('Users/'+str(count)+'/2.wav', audio_data)
        fs.save('Users/'+str(count)+'/3.wav', audio_data)
        fs.save('Users/'+str(count)+'/4.wav', audio_data)
        res = subprocess.check_output('ffmpeg.exe -i '+'Users/'+str(count)+'/1.wav'+" "+'Users/'+str(count)+'/11.wav', shell=True)
        res = subprocess.check_output('ffmpeg.exe -i '+'Users/'+str(count)+'/2.wav'+" "+'Users/'+str(count)+'/12.wav', shell=True)
        res = subprocess.check_output('ffmpeg.exe -i '+'Users/'+str(count)+'/3.wav'+" "+'Users/'+str(count)+'/13.wav', shell=True)
        res = subprocess.check_output('ffmpeg.exe -i '+'Users/'+str(count)+'/4.wav'+" "+'Users/'+str(count)+'/14.wav', shell=True)
        os.remove('Users/'+str(count)+'/1.wav')
        os.remove('Users/'+str(count)+'/2.wav')
        os.remove('Users/'+str(count)+'/3.wav')
        os.remove('Users/'+str(count)+'/4.wav')
        return HttpResponse("Signup Process with Voice Recording Completed", content_type="text/plain")
            

def Signup(request):
    if request.method == 'POST':
        global count
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        count = 0
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
        with db_connection:
            cur = db_connection.cursor()
            cur.execute("select count(*) FROM register")
            rows = cur.fetchall()
            for row in rows:
                count = row[0]
                break
        if os.path.exists('Users/'+str(count)) == False:
            os.mkdir("Users/"+str(count))
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'voiceattendence',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO register(user_id,username,password,contact,email,address) VALUES('"+str(count)+"','"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            context= {'data':'Signup Process Completed'}
            return render(request, 'SignupRecordVoice.html', context)
        else:
            context= {'data':'Error in signup process'}
            return render(request, 'Register.html', context)
