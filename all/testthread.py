#!/usr/bin/env python
#title           :script.py
#description     :This is to test two threads. One updating position and orientation while other sending commands
#author          :Tigmanshu
#date            :18th Oct 2016
#Last modified   :20th Oct 2016
#version         :0.1
#notes           :
#python_version  :2.7.6

import time
import threading

from random import randint
from all.client import VrepClient
from all.car import VrepCar
from all.observer import VrepObserver

# Initialize communication, obtain ID and start simulation
client = VrepClient()
ID = client.start()

# Initialize observer
obs = VrepObserver(ID, 'Vision_sensor')
obs.learningrate = 0.03
obs.debug = True

# Intialize car
pioneer = VrepCar(clientID=ID, leftjoint_name='Pioneer_p3dx_leftMotor', rightjoint_name='Pioneer_p3dx_rightMotor')

def move_car():
    global stop
    while (not stop):
        leftwheelcommand= randint(0,1)
        rightwheelcommand= randint(0,1)
        u=(leftwheelcommand, rightwheelcommand)
        pioneer.command(u)
        # pioneer.command((0.5, 0.5))
        time.sleep(6)


def updatecarinfo():
    global stop
    while (not stop):
        obs.get_orientation()
        print ('Position (x,y) =', obs.position)
        print ('Orientation with +X axis =', obs.orientation)
        time.sleep(1)

global stop
stop = False

thread_move_car=threading.Thread(target=move_car)
thread_updatecarinfo=threading.Thread(target=updatecarinfo)
thread_move_car.start()
# thread_move_car.join()

thread_updatecarinfo.start()

raw_input("Press any key to stop")
stop=True
# disconnect communication and stop simulation
client.stop()
time.sleep(2)
