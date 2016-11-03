#!/usr/bin/env python

import vrep

class Client(object):

    def __init__(self):
        self.ID=None


class VrepClient(Client):
    '''
    This class is a subclass of Client class. Its functions are to connect and disconnect with server
    '''

    IP='127.0.0.1'
    port=19999


    def __init__(self):
        super(VrepClient, self).__init__()


    def start(self):

        '''Connects to specified server via given IP and port, returns an ID and starts simulation'''

        self.ID=vrep.simxStart(self.IP, self.port, True, True, 5000, 5)
        if self.ID != -1:
            print ('Connected to V-REP server')
            _ = vrep.simxStartSimulation(clientID=self.ID, operationMode=vrep.simx_opmode_oneshot_wait)
            if _ == vrep.simx_return_ok:
                print ('Simulation started..')
        else:
            print ('!!!!!!!!!!!!!!!!  Unable to connect to V-REP server  !!!!!!!!!!!!!!!!')
        return self.ID


    def stop(self):

        '''Stops the simulation and disconnects from V-REP server'''

        _ = vrep.simxStopSimulation(clientID=self.ID, operationMode=vrep.simx_opmode_oneshot_wait)
        if _ == vrep.simx_return_ok:
            print ('Simulation stopped')
        _ = vrep.simxFinish(self.ID)

