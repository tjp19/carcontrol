#!/usr/bin/env python

import vrep

class Car(object):
    '''

    This class commands the car.

    '''

    def __init__(self):
        self.ID=None

    def command(self,u):
        '''

        :param u: is a tuple of length 2. (leftwheelcommand, rightwheelcommand)
        :return:

        '''
        pass

    def command_v_w(self, v, w):
        pass


class VrepCar(Car):

    '''

    This subclass (inherited from Car parent class) obtains joint handles of left wheel and right wheel
    for wheeled robot in vrep upon initialization and has command functions for the same. This class implements
    methods to move the car in vrep simulation.

    '''

    def __init__(self, clientID, leftjoint_name, rightjoint_name):
        super(VrepCar, self).__init__()
        self.ID=clientID #ID over which it connects with simulator
        self.leftjoint = leftjoint_name #name of the left joint of corresponding mobile car in vrep
        self.rightjoint = rightjoint_name #name of the left joint of corresponding mobile car in vrep

        #leftjointhandle, rightjointhandle are left and right joint handles (references) to mobile car respectively
        _, self.leftjointhandle = vrep.simxGetObjectHandle(self.ID, self.leftjoint, vrep.simx_opmode_oneshot_wait)
        _, self.rightjointhandle = vrep.simxGetObjectHandle(self.ID, self.rightjoint,
                                                            vrep.simx_opmode_oneshot_wait)

    def command(self, u):
        '''

        This function sends command to wheeled robot in vrep
        :param u: u is control command to left wheel and right wheel as a tuple. u[0]=leftwheel, u[1]=rightwheel
        :return: None

        '''
        vrep.simxSetJointTargetVelocity(self.ID, self.leftjointhandle, u[0], vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetVelocity(self.ID, self.rightjointhandle, u[1], vrep.simx_opmode_oneshot_wait)


    def command_v_w(self, v, w):
        '''

        This function allows to implement commands as a differential drive.
        :param v: linear command
        :param w: angular command
        :return: None

        '''
        vrep.simxSetJointTargetVelocity(self.ID, self.leftjointhandle, v-w, vrep.simx_opmode_oneshot_wait)
        vrep.simxSetJointTargetVelocity(self.ID, self.rightjointhandle, v+w, vrep.simx_opmode_oneshot_wait)


class RealCar(Car):
    def __init__(self):
        super(RealCar, self).__init__()