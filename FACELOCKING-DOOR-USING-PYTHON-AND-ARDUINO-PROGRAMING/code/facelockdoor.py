import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
import serial
import time
import pyttsx3

# Initialize variables
q = 1
x = 0
c = 0
m = 0
d = 0

# Load training data
data_path = 'C:/Users/vicky/OneDrive/Desktop/python/image/'
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
Training_data, Labels = [], []

for i, files in enumerate(onlyfiles):
    image_path = join(data_path, onlyfiles[i])
    images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if images is not None:
        Training_data.append(np.asarray(images, dtype=np.uint8))
        Labels.append(i)

Labels = np.asarray(Labels, dtype=np.int32)

# Train the face recognizer model
model = cv2.face.LBPHFaceRecognizer_create()
model.train(np.asarray(Training_data), np.asarray(Labels))
print("Training complete")

# Load Haar cascade for face detection
face_classifier = cv2.CascadeClassifier('C:/Users/vicky/AppData/Local/Programs/Python/Python311/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
engine.setProperty("rate", 140)
engine.setProperty("volume", 1.0)  # Volume should be between 0.0 and 1.0

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function to detect faces
def face_detector(img, size=0.5):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:  # Corrected condition here
        return img, []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
        roi = img[y:y + h, x:x + w]
        roi = cv2.resize(roi, (200, 200))

    return img, roi

# Start video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    image, face = face_detector(frame)

    try:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        result = model.predict(face)
        if result[1] < 500:
            confidence = int((1 - (result[1] / 300)) * 100)
            display_string = str(confidence)
            cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 0))

            if confidence >= 83:
                cv2.putText(image, "Unlocked", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
                cv2.imshow('Face', image)
                x += 1
            else:
                cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
                cv2.imshow('Face', image)
                c += 1
    except Exception as e:
        print(e)
        cv2.putText(image, "Face not found", (250, 450), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0, 255, 255))
        cv2.imshow('Face', image)
        d += 1

    if cv2.waitKey(1) == 13 or x == 10 or c == 30 or d == 20:
        break

cap.release()
cv2.destroyAllWindows()

# Act based on recognition results
if x >= 5:
    m = 1
    ard = serial.Serial('COM5', 9600)
    time.sleep(2)
    var = 'a'
    c = var.encode()
    speak("Face recognition complete. It is matching with the database. Welcome, sir. Door is opening for 5 seconds.")
    ard.write(c)
    time.sleep(4)
elif c == 30:
    speak("Face is not matching. Please try again.")
elif d == 20:
    speak("Face is not found. Please try again.")

if m == 1:
    speak("Door is closing.")
