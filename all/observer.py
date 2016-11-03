#!/usr/bin/env python

import cv2
import numpy as np
import time

import vrep

class Observer(ImageSource):
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

    The position of the foreground object(car) is (x,y) co-ordinate which is center of the bounding box around the object.
    The orientation of the foreground object(car) is in degrees w.r.t. +X axis

    '''

    def __init__(self):
        self.position = None
        self.orientation = None
        self.fgbg = cv2.BackgroundSubtractorMOG2(history=2, varThreshold=2, bShadowDetection=True)
        self.img = None
        self.debug = False
        self.learningrate = 0.1
        self.videowriter=cv2.VideoWriter('video.avi', fourcc=cv2.cv.CV_FOURCC('M','J','P','G'), fps=10, frameSize=(640, 480))

    def grab_image(self):
        pass

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
                mask = self.fgbg.apply(self.img, learningRate=self.learningrate)
        else:
            self.grab_image()
            mask = self.fgbg.apply(self.img, learningRate=self.learningrate) #apply operator returns 8 bit binary image

        # note that the foreground background segmentation
        # In the image "mask" background=0, foreground=255, shadows=127

        # Hence for thresholding , any threshold value below 127 is fine. 255 would be the value that would be
        # assigned for all values above threshold value specified.

        _, thresh = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
        # thresh = cv2.erode(thresh.copy(), (3, 3), iterations=1)
        # dilated = cv2.dilate(thresh.copy(), (5, 5), iterations=1)

        # TODO : erode, floodfill, find position
        #
        # The mask to be used in floodfill should be 2 pixels wider and 2 pixels taller than the image
        # as mentioned in floodFill (OpenCV documentation)

        im_floodfill = thresh.copy()  # copy thresholded channel
        # Mask for floodFill, size is 2 px wider and 2 px taller than thresholded image
        mask_floodfill=np.zeros((thresh.shape[0] + 2, thresh.shape[1] + 2), np.uint8)
        # flood fill entire thresholded image, enclosed black parts will remain (rest all white)
        cv2.floodFill(im_floodfill,mask_floodfill, (0,0), 255)
        # invert the result of floodfill, which will change the enclosed black parts to be white (rest all black)
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)
        # OR operation with original thresholded image, which will fill the enclosed black holes within it
        finalmask=cv2.bitwise_or(thresh.copy(), im_floodfill_inv)
        # finalmask=cv2.erode(finalmask.copy(), (3,3), iterations=1)
        # finalmask=cv2.dilate(finalmask.copy(), (3,3), iterations=2)


        conts, _ = cv2.findContours(finalmask.copy(), cv2.cv.CV_RETR_EXTERNAL, cv2.cv.CV_CHAIN_APPROX_NONE)


        #TODO: Some noise seen in mask even when car stationary, identified as contours, avoid that

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
            # areas = (0,0) assigned when no contours seen (used in debug to plot previous known position
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

        :return: angle w.r.t. +X axis

        '''

        # TODO: Probably wont need the first block (of when position == None,
        # TODO: (contd..) if we write initial behaviour to identify position and orientation in main program itself

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


class VrepObserver(Observer):
    '''

    The vrepObserver subclass is inherited from Observer parent class. The clientID passed as parameter
    is obtained from instantiation of vrepClient

    '''

    def __init__(self, clientID, visionsensor_name):
        super(VrepObserver, self).__init__()
        self.ID = clientID
        self.visionsensor = visionsensor_name
        _, self.visionhandle = vrep.simxGetObjectHandle(self.ID, self.visionsensor,
                                                        vrep.simx_opmode_oneshot_wait)
        if _ != vrep.simx_return_ok:
            print (' !!!!!! Vision sensor handle not obtained !!!!!!')
        else:
            print ('Obtained vision sensor handle')

    def grab_image(self):
        '''

        This function obtains an image from vision sensor in vrep simulation and returns
        a bgr image and rgb image. Updates the attribute img (cmap=bgr).

        '''

        if self.img == None:
            err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                        vrep.simx_opmode_streaming)
            time.sleep(1)
            err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                        vrep.simx_opmode_buffer)
        else:
            err, res, self.img = vrep.simxGetVisionSensorImage(self.ID, self.visionhandle, 0,
                                                          vrep.simx_opmode_buffer)
        img_rgb = np.array(self.img, dtype='uint8')
        img_rgb.resize([res[1], res[0], 3])
        img_rgb = cv2.flip(img_rgb, 0)
        img_bgr = cv2.cvtColor(img_rgb, cv2.cv.CV_RGB2BGR)
        self.img = img_bgr
        return img_bgr, img_rgb

class ImageSource(object):
    '''
    This class has methods which can return images from different sources. The sources are defined in constructor
    with 0 as default (webcam) or filename
    '''

    def __init__(self, source = 0, filename = None, clientID = None, visionsensor_name = None):
        self.source = source
        self.filename = filename
        self.img = None
        if self.source == 0 :
            self.cap = cv2.VideoCapture(0)
        elif self.source == 'file':
            self.cap = cv2.VideoCapture(self.filename)
        elif self.source == 'simulation':
            self.ID = clientID
            self.visionsensor = visionsensor_name
            _, self.visionhandle = vrep.simxGetObjectHandle(self.ID, self.visionsensor,
                                                            vrep.simx_opmode_oneshot_wait)
            if _ != vrep.simx_return_ok:
                print (' !!!!!! Vision sensor handle not obtained !!!!!!')
            else:
                print ('Obtained vision sensor handle')

    def grab_image(self) :
        '''

        The function acquires an image from the source specified in the constructor. It returns a bgr image
        and updates the attribute self.img
        :return: a bgr image

        '''
        if self.source == 0 or self.source == 'file':
            _, self.img= self.cap.read()
            # print error msg if image not acquired
            if _ != True:
                print ('Image not acquired from image source')
        elif self.source == 'simulation':
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