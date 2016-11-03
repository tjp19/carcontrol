# import numpy as np
#
# a=np.array([0, 0])
# b=np.array([-3, -3])
# Y1=np.max((a[1], b[1]))
# Y2=np.min((a[1], b[1]))
# ans=(Y1-Y2)/np.linalg.norm((b[0]-a[0], b[1]-a[1]))
# print np.arcsin(ans)*(180/np.pi)

# import threading
# import time
#
# def testabc():
#     for i in range(10):
#         print ('Some processing')
#     return
#
# def testxyz():
#     for i in range(10):
#         print ('More processing')
#     return
#
# threads=[]
# t=threading.Thread(target=testabc)
# t1=threading.Thread(target=testxyz)
# t.start()
# t1.start()
# print threading.active_count()

# import cv2
# import time
#
# cap = cv2.VideoCapture(0)
#
# while True:
#     _,frame= cap.read()
#     if _ !=0:
#         cv2.imshow('frame', frame)
#
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
# cap.release()
# cv2.destroyAllWindows()
# print type(frame)
# print frame.shape

# import cv2
# import numpy as np
# cap=cv2.VideoCapture(0)
# fgbg=cv2.BackgroundSubtractorMOG()
# writer=cv2.VideoWriter('output.avi', fourcc=cv2.cv.CV_FOURCC('M','J','P','G'), fps=10, frameSize=(480, 640))
# writermask = cv2.VideoWriter('fgbgseg.avi', fourcc=cv2.cv.CV_FOURCC('M','J','P','G'), fps=10, frameSize=(480, 640), isColor=0)
# while True:
#     _, frame=cap.read()
#     mask=fgbg.apply(frame, learningRate=0.1)
#     thresh=mask
#     im_floodfill = thresh.copy()  # copy thresholded channel
#     # Mask for floodFill, size is 2 px wider and 2 px taller than thresholded image
#     mask_floodfill = np.zeros((thresh.shape[0] + 2, thresh.shape[1] + 2), np.uint8)
#     # flood fill entire thresholded image, enclosed black parts will remain (rest all white)
#     cv2.floodFill(im_floodfill, mask_floodfill, (0, 0), 255)
#     # invert the result of floodfill, which will change the enclosed black parts to be white (rest all black)
#     im_floodfill_inv = cv2.bitwise_not(im_floodfill)
#     # OR operation with original thresholded image, which will fill the enclosed black holes within it
#     finalmask = cv2.bitwise_or(thresh.copy(), im_floodfill_inv)
#     writer.write(frame)
#     writermask.write(mask)
#     cv2.imshow('frame', frame)
#     cv2.imshow('mask', finalmask)
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
# cap.release()
# writer.release()
# print np.max(mask), np.min(mask)


# def opt_fun(x1, x2, *positional_parameters, **keyword_parameters):
#     if ('optional' in keyword_parameters):
#         print 'optional parameter found, it is ', keyword_parameters['optional']
#     else:
#         print 'no optional parameter, sorry'
#
# opt_fun(1,2,optional="optparam")

import cv2
from matplotlib import pyplot as  plt
import time
cap = cv2.VideoCapture('/home/tigmanshu/PycharmProjects/carcontrol/all/video.avi')


while True:
    _, frame=cap.read()
    cv2.imshow('frame', frame)
    time.sleep(0.1)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()