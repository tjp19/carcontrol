#!/usr/bin/env python

import cv2
import numpy as np
import time

import vrep

class Observer():
    '''

    This class determines the position and orientation of a foreground object(car) in an image as seen by observer.
    The origin of the image is top left corner. For a (480,640) image.

    (0,0)----------------------->(640,0)
    |
    |
    |
    |
    |
    |
    V
    (0, 480)

    The position of the foreground object(car) is (x,y) co-ordinate which is center of the bounding box around the object in the image.
    The orientation of the foreground object(car) is in degrees w.r.t. +X axis in the image. (0 to 180 deg, 3rd and 4th quadrant, clockwise)
    (0 to -180 deg, 1st and 2nd quadrant, anticlockwise)

    The type of image source with optional parameters (if needed) must be specified while declaring a class instance.
    If image source = '0' i.e. from webcam, needs no optional parameters
    If image source = 'file', the parameter 'pathtofile' which is path to video file must be specified
    If image source = 'simulation', the parameters 'ID' (clientID of vrep simulation) and 'visionsensor_name' (name of
    vision sensor in vrep simulaton) must be specified.

    '''

    def __init__(self, imagesource = 0, **kwargs):
        self.position = None # position (x,y) co-ordinate is the center of bounding box around the object in the image
        self.orientation = None # orientation of the object w.r.t +X axis (0 to 180 deg, 3rd and 4th quadrant) (0 to -180 deg, 1st and 2nd quadrant)
        self.fgbg = cv2.BackgroundSubtractorMOG()
        self.img = None # image as seen by observer
        self.debug = False
        self.learningrate = 0.1 # learning rate of foreground background model
        self.videowriter=cv2.VideoWriter('video.avi', fourcc=cv2.cv.CV_FOURCC('M','J','P','G'), fps=10,
                                         frameSize=(640, 480))
        self.imagesource = imagesource # 'imagesource' can be '0' (webcam), 'simulation' or 'file'. optional parameters must be provided according to 'imagesource'

        if self.imagesource == 'simulation':
            if ('ID', 'visionsensor_name' in kwargs):
                self.ID = kwargs['ID']
                self.visionsensor = kwargs['visionsensor_name']
                _, self.visionhandle = vrep.simxGetObjectHandle(self.ID, self.visionsensor,
                                                                vrep.simx_opmode_oneshot_wait)
                if _ != vrep.simx_return_ok:
                    print (' !!!!!! Vision sensor handle not obtained !!!!!!')
                else:
                    print ('Obtained vision sensor handle')
            else:
                raise Exception

        elif self.imagesource == 0 :
            self.cap = cv2.VideoCapture(0)

        elif self.imagesource == 'file':
            if ('pathtofile' in kwargs):
                self.filename = kwargs['pathtofile']
            else:
                raise Exception
            self.cap = cv2.VideoCapture(self.filename)
        time.sleep(1)

    def grab_image(self):
        '''

        The function acquires an image from the source specified in the constructor. It returns a bgr image
        and updates the attribute self.img
        :return: a bgr image

        '''

        if self.imagesource == 0 or self.imagesource == 'file':
            _, self.img = self.cap.read()
            # print error msg if image not acquired
            if _ != True:
                print ('Image not acquired from image source')
        elif self.imagesource == 'simulation':
            if self.img == None:
                err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                                   vrep.simx_opmode_streaming)
                time.sleep(1)
                err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                                   vrep.simx_opmode_buffer)
            else:
                err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                                   vrep.simx_opmode_buffer)
                # print error msg if image not acquired
                if err != vrep.simx_return_ok:
                    print ('Image not acquired from image source')
            img_rgb = np.array(self.img, dtype='uint8')
            img_rgb.resize([res[1], res[0], 3])
            img_rgb = cv2.flip(img_rgb, 0)
            img_bgr = cv2.cvtColor(img_rgb, cv2.cv.CV_RGB2BGR)
            self.img = img_bgr
        return self.img

    def get_position(self):
        '''

        Returns the position of the foreground object(car). It acquires the image by itself and
        processes it to obtain position

        :return: position (x,y) co-ordinate, tuple of length 2

        '''

        # if image acquired for first time allow the foreground background model to initialize
        if self.img == None:
            for i in range(0, 20):
                self.grab_image()
                mask = self.fgbg.apply(self.img, learningRate=0.01)
        else:
            self.grab_image()
            mask = self.fgbg.apply(self.img, learningRate=self.learningrate) #apply operator returns 8 bit binary image

        finalmask = cv2.morphologyEx(mask.copy(), cv2.cv.CV_MOP_CLOSE, (5, 5), iterations=2)

        conts, _ = cv2.findContours(finalmask.copy(), cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_SIMPLE)

        #find areas and centers of all contours (if any contours are present)
        centers=[] #empty list initialized to append all centers calculated from contours

        if len(conts) > 0:
            areas = np.array([cv2.contourArea(c) for c in conts])
            areas = np.array(areas)
            np.putmask(areas,areas < 20, 0) # masking areas less than threshold value to eliminate noise
            # The threshold value is approximately 0.04 or 0.05 times minimum size of car blob seen (case when car is
            # farthest in simulation from the camera)

            for c in conts:
                x, y, w, h = cv2.boundingRect(c)
                center = (x+w/2, y+h/2)
                centers.append(center)

            # if all elements in areas array is zero, taking max will still return an index. This should not be
            # the case when there are no areas above a certain threshold (i.e. there is only noise in image)
            # Hence update the position only if any areas are greater than zero.

            if any(areas) != 0:
                # largest contour and corresponding center
                max_index = np.argmax(areas)
                #update position attribute
                self.position = centers[max_index]
        else:
            # if conts not seen then the foreground object has not moved, hence donot update the position
            # areas = np.zeros(1) assigned when no contours seen (used in debug to plot previous known position
            # in absence of any contours and no contour areas greater than threshold)
            areas=np.zeros(1)

        if self.debug:
            self.seeinitialmask = mask
            self.seefinalmask = finalmask
            self.videowriter.write(self.img) # write the image to video to view later
            # draw largest contour and bounding rectangle
            if any(areas) != 0:
                # cv2.drawContours(self.img, conts[max_index], -1, (0, 255, 0), thickness=2)
                x1,y1,w1,h1 = cv2.boundingRect(conts[max_index])
                cv2.rectangle(self.img, (x1,y1), (x1+w1, y1+h1), color=(255,0,0), thickness=3)
                cv2.circle(self.img, (self.position[0], self.position[1]), 5,
                           color=(255, 0, 0), thickness=3)
            else:
                # plot the previously known position when no contours are seen or when no contour areas are greater
                # than threshold
                if self.position != None:
                    cv2.circle(self.img, (self.position[0],self.position[1]), 5,
                               color=(255,0,0), thickness=3)

        return self.position, any(areas) > 0

    def get_orientation(self):

        '''

        calculates the angle in degrees of foreground object(car) with respect to +X axis in 2D.
        It reads the last known position (reads position attribute) and obtains the current position (calls
        get_position method and updates position attribute). These two positions are used to determine angle.

        :return: angle w.r.t. +X axis in the image. (0 to 180 deg, 3rd and 4th quadrant, clockwise)
        (0 to -180 deg, 1st and 2nd quadrant, anticlockwise)

        '''
        if self.orientation == None:
            if self.position == None:
                self.get_position()
                pos1 = self.position
            else:
                pos1 = self.position
        else:
            pos1 = self.position #get last known position

        # get the current position
        self.get_position()
        pos2 = self.position

        # calculate angle if position has changed
        pos1 = np.array(pos1)
        pos2 = np.array(pos2)
        if any(pos1 != pos2):
            u = pos2 - pos1
            unorm = np.linalg.norm(u)
            u = u / unorm
            self.orientation = np.arctan2(u[1], u[0]) * (180 / np.pi)

        if self.debug:
            self.pos1 = pos1
            self.pos2 = pos2

        return self.orientation