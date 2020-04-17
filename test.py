import os
import shutil
import cv2
import numpy as np
from gaze_tracking import GazeTracking
import matplotlib.pyplot as plt
gaze = GazeTracking()

img = cv2.imread('f_45_1.jpg')
gaze.refresh(img)
img = gaze.annotated_frame()
cv2.imshow("gaze", img)
cv2.waitKey(0)  # waits until a key is pressed
cv2.destroyAllWindows()  # d
