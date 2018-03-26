# -*- coding: cp950 -*-
from flask import Flask, request, redirect,render_template, flash, url_for, Response, jsonify
from flask_socketio import SocketIO, emit
from camera import VideoCamera

app = Flask(__name__)
socketio = SocketIO(app)
password ='0000'

video_camera = None
global_frame = None

@app.route('/')
def home():
    return render_template('Login System.html')
     
@app.route("/valid", methods=['POST'])
def valid():
    print request.form['inputUser']
    print request.form['inputPassword']
    print request.environ['REMOTE_ADDR']
    if (request.form['inputPassword']==password):
        return render_template('Control Panel.html')   
    else:
        error = 'Invalid password'
        return render_template('Login System.html', error=error)
   
@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),mimetype='multipart/x-mixed-replace; boundary=frame')

def video_stream():
    global video_camera 
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()
        
    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
         
@socketio.on('webcam_client_event')
def webcam_client_msg(msg):
    print 'webcam '+str(msg['data'])

@socketio.on('ultrasonic_client_event')
def ultrasonic_client_msg(msg):
    print 'ultrasonic '+str(msg['data'])

@socketio.on('log_out')
def log_out():
    print 'logout'

if __name__ == "__main__":
    try:
        socketio.run(app, host='localhost',port=8080,use_reloader=False)
    except:
        print"ip address problem"
    
