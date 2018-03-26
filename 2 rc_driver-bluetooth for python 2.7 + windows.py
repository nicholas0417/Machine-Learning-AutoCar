from PyQt4 import QtGui, QtCore
from threading import Thread
import SocketServer
import serial
import bluetooth
import cv2
import numpy as np
import math
import socket
import webbrowser
import sys

# distance data measured by ultrasonic sensor
sensor_data = " "

class NeuralNetwork(object):

    def __init__(self):
        self.model = cv2.ANN_MLP()

    def create(self):
        layer_size = np.int32([38400, 32, 4])
        self.model.create(layer_size)
        self.model.load('mlp_xml/4_25_OK_version2_mlp.xml')

    def predict(self, samples):
        ret, resp = self.model.predict(samples)
        return resp.argmax(-1)


class RCControl(object):

    def __init__(self):
        #self.serial_port = serial.Serial('COM3', 115200, timeout=1)
        try:
            self.bd_addr = "98:D3:31:FB:50:82"
            self.port = 1
            self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.connect((self.bd_addr, self.port))
        except IOError as ioex:
            print "Couldnt connect with the bluetooth"
            
    def steer(self, prediction):
        try:
            if prediction == 2:
                #self.serial_port.write(chr(1))
                self.sock.send('1')
                print("Forward")
            elif prediction == 0:
                #self.serial_port.write(chr(7))
                self.sock.send('7')
                print("Left")
            elif prediction == 1:
                #self.serial_port.write(chr(6))
                self.sock.send('6')
                print("Right")
            else:
                self.stop()
        except IOError as ioex:
            print "Couldnt connect with the bluetooth"
        except:
            self.sock.close()

    def stop(self):
        #self.serial_port.write(chr(0))
        self.sock.send('0')

class DistanceToCamera(object):

    def __init__(self):
        # camera params
        self.alpha = 8.0 * math.pi / 180
        self.v0 = 117.703270893
        self.ay = 416.077691832

    def calculate(self, v, h, x_shift, image):
        # compute and return the distance from the target point to the camera
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        if d > 0:
            cv2.putText(image, "%.1fcm" % d,
                (image.shape[1] - x_shift, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return d


class ObjectDetection(object):

    def __init__(self):
        self.red_light = False
        self.green_light = False
        self.yellow_light = False

    def detect(self, cascade_classifier, gray_image, image):

        # y camera coordinate of the target point 'P'
        v = 0

        # minimum value to proceed traffic light state validation
        threshold = 150     
        
        # detection
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # draw a rectangle around the objects
        for (x_pos, y_pos, width, height) in cascade_obj:
            cv2.rectangle(image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), (255, 255, 255), 2)
            v = y_pos + height - 5
            #print(x_pos+5, y_pos+5, x_pos+width-5, y_pos+height-5, width, height)

            # stop sign
            if width/height == 1:
                cv2.putText(image, 'STOP', (x_pos, y_pos-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # traffic lights
            else:
                roi = gray_image[y_pos+10:y_pos + height-10, x_pos+10:x_pos + width-10]
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
                
                # check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)
                    
                    # Red light
                    if 1.0/8*(height-30) < maxLoc[1] < 4.0/8*(height-30):
                        cv2.putText(image, 'Red', (x_pos+5, y_pos-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.red_light = True
                    
                    # Green light
                    elif 5.5/8*(height-30) < maxLoc[1] < height-30:
                        cv2.putText(image, 'Green', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        self.green_light = True
    
                    # yellow light
                    #elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
                    #    cv2.putText(image, 'Yellow', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    #    self.yellow_light = True
        return v


class SensorDataHandler(QtCore.QThread):

    data = " "
    daemon=True
    
    def __init__(self, host,parent=None):
        super(SensorDataHandler, self).__init__(parent) #super(SensorDataHandler,self).__init__()
        self.host = host
        self.exiting=False
        
    def shutdown(self):
        self.exiting=True
        self.quit()
        
    def run(self):
        global capturing
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.host, 8002))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()

        global sensor_data
        
        try:
            while (self.data): # self.data
                self.data = self.connection.recv(1024)
                try:
                    sensor_data = round(float(self.data), 1)
                except:
                    break
                #print "{} sent:".format(self.client_address[0])
                print sensor_data
                if(self.exiting):
                    break
        finally:
            print "Connection closed on thread 2"
            self.connection.close()
            self.server_socket.close()
        
            
class VideoStreamHandler(QtCore.QThread):
    
    # h1: stop sign
    h1 = 15.5 - 10  # cm
    # h2: traffic light
    h2 = 15.5 - 10

    # create neural network
    model = NeuralNetwork()
    model.create()

    obj_detection = ObjectDetection()
    rc_car = RCControl()

    # cascade classifiers
    stop_cascade = cv2.CascadeClassifier('cascade_xml/stop_sign.xml')
    light_cascade = cv2.CascadeClassifier('cascade_xml/traffic_light.xml')

    d_to_camera = DistanceToCamera()
    d_stop_sign = 25
    d_light = 25

    stop_start = 0              # start time when stop at the stop sign
    stop_finish = 0
    stop_time = 0
    drive_time_after_stop = 0

    daemon=True
    
    def __init__(self, host,parent=None):
        super(VideoStreamHandler, self).__init__(parent)
        self.host = host
        self.exiting=False
        
    def shutdown(self):
        self.exiting=True
        self.quit()
        #self.terminate()
        
    def run(self):
        global sensor_data
        
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.host, 8000))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')

        stream_bytes = ' '
        stop_flag = False
        stop_sign_active = True
        
        # stream video frames one by one
        try:
            while not self.exiting:
                #stream_bytes += self.rfile.read(1024)
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find('\xff\xd8')
                last = stream_bytes.find('\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_UNCHANGED)

                    # lower half of the image
                    half_gray = gray[120:240, :]
                    
                    # object detection
                    v_param1 = self.obj_detection.detect(self.stop_cascade, gray, image)
                    v_param2 = self.obj_detection.detect(self.light_cascade, gray, image)
                    
                    # distance measurement
                    if v_param1 > 0 or v_param2 > 0:
                        d1 = self.d_to_camera.calculate(v_param1, self.h1, 300, image)
                        d2 = self.d_to_camera.calculate(v_param2, self.h2, 100, image)
                        self.d_stop_sign = d1
                        self.d_light = d2
                    
                    cv2.imshow('image', image)
                    #cv2.imshow('mlp_image', half_gray)
                    
                    # reshape image
                    image_array = half_gray.reshape(1, 38400).astype(np.float32)
                    
                    # neural network makes prediction
                    prediction = self.model.predict(image_array)

                    # stop conditions
                    if sensor_data is not None and sensor_data < 30:
                        print("Stop, obstacle in front")
                        self.rc_car.stop()
                    
                    elif 0 < self.d_stop_sign < 25 and stop_sign_active:
                        print("Stop sign ahead")
                        self.rc_car.stop()

                        # stop for 5 seconds
                        if stop_flag is False:
                            self.stop_start = cv2.getTickCount()
                            stop_flag = True
                        self.stop_finish = cv2.getTickCount()

                        self.stop_time = (self.stop_finish - self.stop_start)/cv2.getTickFrequency()
                        print "Stop time: %.2fs" % self.stop_time

                        # 5 seconds later, continue driving
                        if self.stop_time > 5:
                            print("Waited for 5 seconds")
                            stop_flag = False
                            stop_sign_active = False

                    elif 0 < self.d_light < 30:
                        #print("Traffic light ahead")
                        if self.obj_detection.red_light:
                            print("Red light")
                            self.rc_car.stop()
                        elif self.obj_detection.green_light:
                            print("Green light")
                            pass
                        elif self.obj_detection.yellow_light:
                            print("Yellow light flashing")
                            pass
                        
                        self.d_light = 30
                        self.obj_detection.red_light = False
                        self.obj_detection.green_light = False
                        self.obj_detection.yellow_light = False

                    else:
                        self.rc_car.steer(prediction)
                        self.stop_start = cv2.getTickCount()
                        self.d_stop_sign = 25

                        if stop_sign_active is False:
                            self.drive_time_after_stop = (self.stop_start - self.stop_finish)/cv2.getTickFrequency()
                            if self.drive_time_after_stop > 5:
                                stop_sign_active = True

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.rc_car.stop()
                        break

        finally:
            print "Connection closed on thread 1"
            self.exiting = True
            self.connection.close()
            self.server_socket.close()
            cv2.destroyAllWindows()
            
            
                                         
class Window(QtGui.QWidget):
    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setWindowTitle('Control Panel')
        self.setGeometry(100,100,200,200)

        self.btn0 = QtGui.QPushButton('Searching ip',self)
        self.btn0.clicked.connect(self.searching)
        
        self.btn1 = QtGui.QPushButton('login',self)
        self.btn1.clicked.connect(self.login)

        self.btn2 = QtGui.QPushButton('Start',self)
        self.btn2.clicked.connect(self.startDriving)

        self.btn3 = QtGui.QPushButton('End',self)
        self.btn3.clicked.connect(self.closeDriving)  

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.btn0)
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        vbox.addWidget(self.btn3)

        self.show()
        self.searching()
        
    def searching(self):
        global capturing
        capturing = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.1.1", 80))
            self.host = s.getsockname()[0]
            s.close()
        except IOError as ioex:
            print "Couldnt connect with the Router"
        print('The local ip is: '+self.host)
        
    def login(self):
        try:
            Rpi_IP = socket.gethostbyname('project-rpi') # pi ip
            print ('The rpi ip is: '+Rpi_IP)
            webbrowser.open_new("http://"+str(Rpi_IP)+":8080")
        except: #webbrowser.Error
            print "The Rpi server is not ready"

    def startDriving(self):
        print "pressed start"
        
        self.senser = SensorDataHandler(self.host,)
        self.video = VideoStreamHandler(self.host,)
        if not self.senser.isRunning():
            self.senser.daemon=True
            self.senser.start()
            
        if not self.video.isRunning():
            self.video.daemon=True
            self.video.start()
    def closeDriving(self):
        print "pressed End"
        self.video.exiting = True
        self.senser.exiting = True

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

    
