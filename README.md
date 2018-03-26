# Machine-Learning-AutoCar
--------------------------
## A. In PC (Personal Computer) Side

PC is the server which deals with the information on the image, ultrasonic measurements data by Raspberry pi and throughout using Bluetooth
connectionless to control our remote control car.


## B. In Rpi(Raspberry pi3) Side

On the side of Raspberry Pi we get the image data on the webcam and ultrasonic measurement data and through the socket to the PC side.


## C. Remote Control(Arduino)

The remote control circuit is connected to Arduino and is controlled by Bluetooth.


## D. Tools

Tools we need to prepare and used.
1) Socket programming / multithread TCP server
2) Pygame / Pyserial (we first use USB to control)/ Pyblue:
3) Opencv (Correction / identification of traffic lights / identification stop flag / judgment distance )
4) ANN (Collect training materials in to .npz files after prediction coexistence in xml format parameters)

## E. How to use it

1. in Computer side.
 * a website page which broadcasts the image while  the Autocar was self-driving
 * mlp/xml : the training data we trained
 * training learning : mpl/training & mlp/predict
 * training : collect training data
 * ip search
 
2. in Raspberry pi side :
 * New rpi client with flask
 
3. in Arduino side :
 * Logic bluetooth for car resistor

### Youtube Link :  https://youtu.be/7X3QvIdIIkQ

<a href="http://www.youtube.com/watch?feature=player_embedded&v=7X3QvIdIIkQ
" target="_blank"><img src="http://img.youtube.com/vi/7X3QvIdIIkQ/0.jpg"
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
