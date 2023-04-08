import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime 
import win32com.client as w
import time
import csv

names=[]
with open('namelist2.csv','r') as csv_file:
    csv_reader=csv.reader(csv_file)
    for line in csv_reader:
        names.append(line[0])

strength=len(names)
		 

url = "http://192.168.97.170:8080/video"
vid=cv2.VideoCapture(0)



imagearray=[0]*strength
encodingarray=[0]*strength

for j in range (strength):
    '''speaker.Speak("Enter the name of the student")
    title=input("Enter the name of the student : ")'''
    title=names[j]
    imagearray[j]=face_recognition.load_image_file(f'faces/{title}.jpg')   
    encodingarray[j]=face_recognition.face_encodings(imagearray[j])[0]
    



known_face_encodings=[]
known_face_names=[]
for j in range (strength):
    known_face_encodings.append(encodingarray[j])
    known_face_names.append(names[j])



students=known_face_names.copy()

# the below two lists are for text to speech
present=[]
timing=[]

#the below 4 lines of code is uswd fo the frame or face that is comming from the webcam 
face_locations=[]
face_encodings=[]
face_names=[]
s=True

#the below two lines of code is to get date 
now=datetime.now()
current_date=now.strftime("%Y-%m-%d")

#creating an excell file
f=open(current_date+'.csv','w+',newline='')
lnwriter=csv.writer(f)


while True:
    istrue,frame=vid.read()
    #small_frame=cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
    small_frame=frame
    
    rgb_small__frame=small_frame[:,:,::-1]
    if s:
        face_locations=face_recognition.face_locations(rgb_small__frame)
        face_encodings=face_recognition.face_encodings(rgb_small__frame,face_locations)
        face_names=[]
        for face_encoding in face_encodings:
            matches=face_recognition.compare_faces(known_face_encodings,face_encoding)
            name=""
            face_distance=face_recognition.face_distance(known_face_encodings,face_encoding)
            best_match_index=np.argmin(face_distance)
            if matches[best_match_index]:
                name=known_face_names[best_match_index]
            face_names.append(name)
            if name in students:
                students.remove(name)
                print(students)
                current_time=now.strftime("%H:%M:%S")
                lnwriter.writerow([name,current_time]) #Daata to data base name -> student name && time is current_time
                present.append(name)
                timing.append(current_time)

    cv2.imshow("attendance system",frame)
    if cv2.waitKey(10)==ord('q'):
        break


vid.release()
cv2.destroyAllWindows()
f.close()

speaker=w.Dispatch("SAPI.SpVoice")
n=len(present)
for i in range (n):
    text=f'{present[i]} has given his attendance at time {timing[i]}'
    speaker.Speak(text)
    time.sleep(1)

speaker.Speak("We have stopped taking attendance from now,i am both sad and mad at you students")