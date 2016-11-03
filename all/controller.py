class Controller(object):
    def __init__(self, setpoint):
        self.setpoint = setpoint  # setpoint or reference value
        pass

class PID (Controller):

    '''
    This class inherits from Controller parent class and implements a discrete PID controller
    '''

    def __init__(self, Kp, Ki, Kd, setpoint, tolerance ,**kwargs):
        super(PID, self).__init__(setpoint)
        self.Kp=Kp # Proprotional gain
        self.Ki=Ki # Integral gain
        self.Kd=Kd # Derivative gain
        self.tolerance = tolerance # +/- error tolerance
        self.err_previous=0 # error at previous time instant
        self.err=0 # error at current time instant
        self.u = 0 # control output from PID controller
        if ('Imax', 'Imin' in kwargs):
            self.Imax = kwargs['Imax']
            self.Imin = kwargs ['Imin']
        else:
            raise Exception
    def update(self, fb_value):
        '''
        This method calculates the control output for given setpoint and feedback value

        :param fb_value: feedback value of measured variable
        :return: u : controller output
        '''
        self.err = self.setpoint - fb_value
        integral_component=self.Ki * (self.err_previous + self.err)

        if abs(self.err) > self.tolerance :
            if integral_component > self.Imax:
                integral_component = self.Imax
            elif integral_component < self.Imin:
                integral_component = self.Imin

            self.u = self.Kp*self.err + integral_component \
                     + self.Kd * (self.err-self.err_previous)
            self.err_previous = self.err
        else:
            self.u = 0
        return self.u