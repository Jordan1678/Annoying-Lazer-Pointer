import cv2


from flask import Flask, render_template, Response


camera = cv2.VideoCapture(0)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# A function to generate the frames from the camera and make them a video
def gen():
    # get camera
    cap = cv2.VideoCapture(0)

    # horizontal/vertical resolution cap for a raspberry pi I suggest
    # 480p over 720p because the raspberry pi 3 b+ (The one I'm using)
    # doesn't have enough compute power to render frames at a steady
    # frame rate
    cap.set(3, 640)  # vertical cap
    cap.set(4, 480)  # horizontal cap

    # Read until frame is completed
    while (cap.isOpened()):

        # Capture frame-by-frame
        ret, img = cap.read()

        # this is where if you want to draw on frames you add that here
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
