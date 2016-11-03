#!/usr/bin/env python
# title           :script.py
# description     :This will control a car based on video frame information
# author          :Tigmanshu
# date            :01st Nov 2016
# Last modified   :1st Nov 2016
# version         :0.1
# usage           :python scriptcontrol.py
# notes           :
# python_version  :2.7.6

import cv2
import time
import numpy as np

from matplotlib import pyplot as plt
from all.client import VrepClient
from all.car import VrepCar
from all.observerv1 import Observer
from all.controller import PID

# Initialize a videowriter object in script to see what observer tracked
track=cv2.VideoWriter('observertracking.avi', fourcc=cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps=10, frameSize=(640, 480))
trackmask=cv2.VideoWriter('observertrackmask.avi', fourcc=cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps=10, frameSize=(640, 480), isColor=0)

# Decide on image source
imagesource = 'simulation'
debug = True

if imagesource == 'simulation':

    # Initialize communication, obtain ID and start simulation
    client = VrepClient()
    ID = client.start()

    # Initialize observer
    obs=Observer(imagesource=imagesource, ID=ID, visionsensor_name='Vision_sensor')
    obs.debug = debug

    # Intialize car
    pioneer = VrepCar(clientID=ID, leftjoint_name='Pioneer_p3dx_leftMotor', rightjoint_name='Pioneer_p3dx_rightMotor')

    #obtain initial position
    if obs.position == None:
        obs.get_position() # call position for first time to initialize foreground background model
        pioneer.command((-1, 1))
        time.sleep(0.5)
        obs.get_position()
        pioneer.command((0, 0))
        if obs.debug:
            cv2.imwrite('initial_pos_mask.jpg', obs.seefinalmask)
    print ('Initial position', obs.position)

    #obtain initial orientation
    if obs.orientation == None:
        pioneer.command((-1, -1))
        time.sleep(2)
        pioneer.command((0, 0))
        obs.get_position()
        obs.get_position()
        if obs.debug:
            cv2.imwrite('pos1_mask_for_ort.jpg', obs.seefinalmask)
        pioneer.command((1, 1))
        time.sleep(2)
        pioneer.command((0, 0))
        obs.get_orientation()
        if obs.debug:
            cv2.imwrite('pos2_mask_for_ort.jpg', obs.seefinalmask)
        pioneer.command((0, 0))
    print ('Initial orientation', obs.orientation)
    initial_pos1 = obs.pos1
    initial_pos2 = obs.pos2
    print ('initial_pos_1', initial_pos1)
    print ('initial_pos_2', initial_pos2)

    pioneer.command((1, 1))
    time.sleep(1)

elif imagesource == 0:
    obs = Observer(imagesource=imagesource)
    obs.debug = debug

elif imagesource == 'file':
    obs = Observer(imagesource=imagesource, pathtofile ='/home/tigmanshu/PycharmProjects/carcontrol/all/samplevideo.avi')
    obs.debug = debug

obs.learningrate = 0.1

# set goal position
goal_pos=()
# obtain position and orientation continuously
while True:
    time.sleep(0.2)

    obs.get_orientation()
    print
    print ('Position (x,y) =', obs.position)
    print ('Orientation with +X axis =', obs.orientation)
    print

    if obs.imagesource == 'simulation':
        pass
    if obs.debug:
        cv2.imshow('Observer view', obs.img)
        cv2.imshow('Mask', obs.seeinitialmask)
        cv2.imshow('Processed mask', obs.seefinalmask)
        track.write(obs.img)
        trackmask.write(obs.seefinalmask)

    if cv2.waitKey(1) & 0xFF == 27:
        break

if imagesource == 'simulation':
    pioneer.command((0, 0))
if imagesource == 'file' or 0:
    obs.cap.release()

if obs.debug:

    # display the latest acquired image and position
    fig0, ax0 = plt.subplots()
    ax0.imshow(obs.img)
    ax0.scatter(obs.position[0], obs.position[1], s=60)

    # display the points used to identify orientation
    fig1, ax1 = plt.subplots()
    ax1.imshow(obs.img)
    ax1.scatter([obs.pos1[0], obs.pos2[0]], [obs.pos1[1], obs.pos2[1]], s=60, c='r')

    #display points by which initial orientation was identified
    fig2, ax2 = plt.subplots()
    ax2.imshow(obs.img)
    ax2.scatter(initial_pos1[0], initial_pos1[1], s=60, c='g')
    ax2.scatter(initial_pos2[0], initial_pos2[1], s=60, c='y')

    plt.show()


cv2.destroyAllWindows()
track.release()
trackmask.release()

if imagesource == 'simulation':
    # disconnect communication and stop simulation
    client.stop()
