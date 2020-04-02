import numpy as np
import cv2


class Pupil(object):
    """
    This class detects the iris of an eye and estimates
    the position of the pupil
    """

    def __init__(self, eye_frame, threshold, side):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None
        self.dict = {0:{0:[0.5], 1:[0.5]}, 1:{0:[0.5], 1:[0.5]}}

        self.detect_iris(eye_frame, side)

    @staticmethod
    def image_processing(eye_frame, threshold):
        """Performs operations on the eye frame to isolate the iris

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
            threshold (int): Threshold value used to binarize the eye frame

        Returns:
            A frame with a single element representing the iris
        """
        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15)
        new_frame = cv2.erode(new_frame, kernel, iterations=3)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]

        return new_frame

    def detect_iris(self, eye_frame, side):
        """Detects the iris and estimates the position of the iris by
        calculating the centroid.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
        """
        self.iris_frame = self.image_processing(eye_frame, self.threshold)

        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        # print(len(contours), contours)
        cv2.drawContours(eye_frame, contours, -1, (0,255,0), 3)
        contours = sorted(contours, key=cv2.contourArea)

        # cv2.imshow("Iris Contour", eye_frame)

       # print(contours)

        try:
            moments = cv2.moments(contours[-2])
            self.x = int(moments['m10'] / moments['m00'])
            self.y = int(moments['m01'] / moments['m00'])
            self.dict[side][0].append(self.x)
            self.dict[side][1].append(self.y)
        except (IndexError, ZeroDivisionError):
            self.x = int(np.mean(self.dict[side][0]))
            self.y = int(np.mean(self.dict[side][1]))

        cv2.line(eye_frame, (self.x - 5, self.y), (self.x + 5, self.y), (0, 255, 0))
        cv2.line(eye_frame, (self.x, self.y - 5), (self.x, self.y + 5), (0, 255, 0))

