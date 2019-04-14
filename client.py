import time
from random import randrange
from socketIO_client import SocketIO, LoggingNamespace
import os
import pickle
import cv2
import math
import numpy as np
import http.client, urllib.request, urllib.parse, urllib.error, base64
import io
import pandas as pd
import json
from sklearn.preprocessing import StandardScaler
from socketIO_client import SocketIO, LoggingNamespace
from datetime import datetime

DATE_FMT = "%Y-%m-%d %H:%M:%S"
headers = {
    # Request headers
     'Content-type': 'application/octet-stream', #the content type can be changed by the picture file
    'Ocp-Apim-Subscription-Key': '7d00c8585b384ab49c4f8a5c7b4e5abb'
}
params = urllib.parse.urlencode({
# Request parameters
'returnFaceId': 'true',
'returnFaceLandmarks': 'true',
'returnFaceAttributes': 'age,gender,emotion,smile,hair,makeup,headPose'
})
expression = ['Not Confused', 'Confused']
targetLandmarks = ["eyebrowLeftOuter","eyebrowLeftInner","eyebrowRightInner","eyebrowRightOuter"]

def processing(df):
    df['OuterGap'] = abs(df.eyebrowLeftOuter_x - df.eyebrowRightOuter_x)/df.width
    df['InnerGap'] = abs(df.eyebrowLeftInner_x - df.eyebrowRightInner_x)/df.width
    df['roll'] = abs(df.roll)
    df['yaw'] = abs(df.roll)
    df['surprise'] = -df.surprise
    df['bad_feeling'] = df.disgust + df.fear 
    df['Gap'] = -(df.OuterGap + df.InnerGap)
    df = df[[ 'surprise', 'Gap','yaw', 'roll','sadness','bad_feeling', 'anger','contempt']]
    return df

def toBytes():
    breaks = False
    cv2.waitKey(500)
    rval, frame = cap.read()
    if (rval != True):
        breaks = True 
    encoded_image = cv2.imencode(".jpg", frame)[1]
    img = encoded_image.tobytes()
    return breaks, img

def processToDF(data):
    dataframe = []
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    for face in data:
        dicts = {}
        for emotion, value in face['faceAttributes']['emotion'].items():
            dicts[emotion] = value
        for pose, value in face['faceAttributes']['headPose'].items():
            dicts[pose] = value
        for landmark in face['faceLandmarks'].keys():
            if landmark in targetLandmarks:
                dicts[landmark+'_x'] = face["faceLandmarks"][landmark]["x"]
        for position in face['faceRectangle'].keys():
            if position in ['left','width']:
                dicts[position] = face['faceRectangle'][position]
        dataframe.append(dicts)
    dataframe = pd.DataFrame(dataframe)
    return dataframe 

if __name__ == '__main__':
    cur_dir = os.path.dirname(__file__)
    classifier = pickle.load(open(
                    os.path.join(cur_dir,
                    'pkl_objects',
                    'classifier_new.pkl'), 'rb'))
    
    url = 'http://172.31.100.130:8080/video'
    count = 0 
    cv2.namedWindow("frame")
    cap = cv2.VideoCapture(url)

    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    store = []
    with SocketIO('localhost', 8000, LoggingNamespace) as socketIO:
        while True:
            breaks, img = toBytes()
            count += 1
            print(img)
            if breaks:
                break
            try:
                conn.request("POST", "/face/v1.0/detect?%s" % params, img, headers)
                response = conn.getresponse()
                data = response.read()
            except Exception as e:
                print("[Errno {0}] {1}".format(e.errno, e.strerror))

            dataframe = processToDF(data)
            try:
                dataframe = processing(dataframe)
                result = classifier.predict_proba(dataframe)
                result = [i[1] for i in result]
                result = sum(result)/len(result)
                store.append(result) 
                #print(store)
                #print(result)
            except:
                pass

            if count % 3 == 0 and store:
                print(6)
                datetime_now = datetime.now().strftime(DATE_FMT)
                send_data = {
                'x' : [datetime_now],
                'y1' : [round(sum(store)/len(store)*100,2)],
                'y2' : [50]
                }
                socketIO.emit('my_event', send_data)
                store = []
            if cv2.waitKey(1) & 0xFF == ord('q'):
                conn.close()
                break
    cap.release()
    cv2.destroyAllWindows()




