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
    'Ocp-Apim-Subscription-Key': '6236be845a4448c1b1b2111d516c7b00'
}
params = urllib.parse.urlencode({
# Request parameters
'returnFaceId': 'true',
'returnFaceLandmarks': 'false',
'returnFaceAttributes': 'age,gender,emotion,smile,hair,makeup,headPose'
})
expression = ['Not Confused', 'Confused']

def processing(df):
    df['roll'] = abs(df.roll)
    df['yaw'] = abs(df.roll)
    df['happiness'] = -df.happiness
    df['bad_feeling'] = df.sadness + df.anger + df.disgust + df.fear + df.sadness + df.surprise
    df = df[['happiness', 'neutral', 'roll', 'yaw', 'bad_feeling']]
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
        dataframe.append(dicts)
    dataframe = pd.DataFrame(dataframe)
    return dataframe 

#Main Begins:
if __name__ == '__main__':
    cur_dir = os.path.dirname(__file__)
    classifier = pickle.load(open(
                    os.path.join(cur_dir,
                    'pkl_objects',
                    'classifier.pkl'), 'rb'))

    cv2.namedWindow("frame")
    cap = cv2.VideoCapture(0)

    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    with SocketIO('localhost', 8000, LoggingNamespace) as socketIO:
        while True:
            breaks, img = toBytes()
            if breaks:
                break

            try:
                conn.request("POST", "/face/v1.0/detect?%s" % params, img, headers)
                response = conn.getresponse()
                data = response.read()
            except Exception as e:
                print("[Errno {0}] {1}".format(e.errno, e.strerror))

            dataframe = processToDF(data)

            if 'roll' in dataframe.columns and 'pitch' in dataframe.columns:
                dataframe = processing(dataframe)
                result = classifier.predict_proba(dataframe)
                result = [value[1]/len(result) for value in result]
                datetime_now = datetime.now().strftime(DATE_FMT)
                send_data = {
                'x' : [datetime_now],
                'y1' : [round(sum(result)*100,2)],
                'y2' : [50]
                }
                socketIO.emit('my_event', send_data)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                conn.close()
                break
    cap.release()
    cv2.destroyAllWindows()




