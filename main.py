import cv2
import Rpi.GPIO as GPIO

from flask import Flask, render_template, Response

Base = 12
Arm = 13

camera = cv2.VideoCapture(0)
app = Flask(__name__)

GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Base, GPIO.OUT)
GPIO.setup(Arm, GPIO.OUT)

BasePWM = GPIO.PWM(Base, 50)
ArmPWM = GPIO.PWM(Arm, 50)
BasePWM.start(0)
ArmPWM.start(0)

def map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

@app.route('/')
def index():
    return render_template('index.html')


# A function to generate the frames from the camera and make them a video
def gen():
    # get camera
    cap = cv2.VideoCapture(0)

    cap.set(3, 640)  # vertical cap
    cap.set(4, 480)  # horizontal cap

    # Read until frame is completed
    while (cap.isOpened()):

        # Capture frame-by-frame
        ret, img = cap.read()
        
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        face = face_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=4)
        
        for (x, y, w, h) in face:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.circle(img, (x+w/2, y+h/2), 5, (255, 0, 255), 5)
            
            BaseTarget = map(x + w/2, 0, 640, 90+45, 90-45)
            ArmTarget = map(y + h/2, 0, 480, 90-32, 90+32)
            
            print(f"Face Found @ {BaseTarget}x {ArmTarget}y"))
            
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=1, fy=1)
            
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        else:
            break


# responds with the generated frames
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(host='0.0.0.0', port=80)
