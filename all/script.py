#!/usr/bin/env python
# title           :script.py
# description     :This will control a car based on video frame information
# author          :Tigmanshu
# date            :17th Oct 2016
# Last modified   :27th Oct 2016
# version         :0.1
# usage           :python script.py
# notes           :
# python_version  :2.7.6

import cv2
import time

from matplotlib import pyplot as plt
from all.client import VrepClient
from all.car import VrepCar
from all.observer import VrepObserver

# Initialize communication, obtain ID and start simulation
client = VrepClient()
ID = client.start()

# Initialize observer
obs = VrepObserver(ID, 'Vision_sensor')
obs.learningrate = 0.1
obs.debug = True

# Initialize a videowriter object in script to see what observer tracked
track=cv2.VideoWriter('observertracking.avi', fourcc=cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps=10, frameSize=(640, 480))
trackmask=cv2.VideoWriter('observertrackmask.avi', fourcc=cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps=10, frameSize=(640, 480), isColor=0)

# Intialize car
pioneer = VrepCar(clientID=ID, leftjoint_name='Pioneer_p3dx_leftMotor', rightjoint_name='Pioneer_p3dx_rightMotor')

#obtain initial position
if obs.position == None:

    # calling this for first time will initialize background model (Nothing in motion at this
    # point of time in simulation
    obs.get_position()

    #start to rotate the car on the same position for some fixed time
    pioneer.command((-1, 1))
    time.sleep(2)

    obs.get_position() #get the position

    pioneer.command((0, 0)) #stop car rotation

    initial_pos=obs.position #save initial position
    print ('Initial position', obs.position)

    # save the processed image used to identify initial position
    if obs.debug == True:
        cv2.imwrite('initial_pos_mask.jpg', obs.seefinalmask)

#obtain initial orientation
if obs.orientation == None:

    # move the car backward for some fixed time
    pioneer.command((-1, -1))
    time.sleep(2)

    # get the position
    obs.get_position()

    # save the processed image used to identify position 1 for orientation
    if obs.debug == True:
        cv2.imwrite ('initial_ort_pos1_mask.jpg', obs.seefinalmask)

    # move the car forward for same fixed time
    pioneer.command((1, 1))
    time.sleep(2)

    # now since the position 1 was obtained earlier, get orientation would also obtain current position and
    # use both of these position to identify initial orientation orientation
    obs.get_orientation()

    # stop the car
    pioneer.command((0, 0))

    # save the initial orientation
    initial_ort = obs.orientation

    print ('Initial orientation', obs.orientation)

    # save the processed image used to identify current position (position 2) for orientation
    if obs.debug == True:
        cv2.imwrite('initial_ort_pos2_mask.jpg', obs.seefinalmask)


pioneer.command((0, 0))
time.sleep(0.5)

# obtain position and orientation continuously
while True:
    time.sleep(0.3)

    # get orientation method uses previous known position and also updates current position of car. Hence using
    # only get orientation method in a loop would be sufficient to obtain current position and orientation

    obs.get_orientation()

    print
    print ('Position (x,y) =', obs.position)
    print ('Orientation with +X axis =', obs.orientation)
    print

    if obs.debug:
        cv2.imshow('Observer view', obs.img)
        cv2.imshow('Mask', obs.seeinitialmask)
        cv2.imshow('Processed mask', obs.seefinalmask)
        track.write(obs.img)
        trackmask.write(obs.seefinalmask)

    if cv2.waitKey(1) & 0xFF == 27:
        break

pioneer.command((0, 0))

# save the last mask seen
cv2.imwrite('lastseen_mask.jpg', obs.seefinalmask)
if obs.debug:

    # display the latest acquired image and position
    fig0, ax0 = plt.subplots()
    ax0.imshow(obs.img)
    ax0.scatter(obs.position[0], obs.position[1], s=60)
    # ax0.scatter(initial_pos[0], initial_pos[1], s=60, c='g')

    # display the points used to identify orientation
    fig1, ax1 = plt.subplots()
    ax1.imshow(obs.img)
    ax1.scatter([obs.pos1[0], obs.pos2[0]], [obs.pos1[1], obs.pos2[1]], s=60, c='r')

    plt.show()


cv2.destroyAllWindows()
track.release()
trackmask.release()

# disconnect communication and stop simulation
client.stop()
