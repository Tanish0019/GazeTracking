import os
import cv2
import numpy as np
from gaze_tracking import GazeTracking
import matplotlib.pyplot as plt

gaze = GazeTracking()


def calc_pupil_deviation(pupil_coords, ideal_coords, frame_dimensions):
    x1 = ideal_coords[0] / frame_dimensions[0]
    x2 = pupil_coords[0] / frame_dimensions[0]
    y1 = ideal_coords[1] / frame_dimensions[1]
    y2 = pupil_coords[1] / frame_dimensions[1]
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_ideal_points(url):
    cap = cv2.VideoCapture(url)
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and frame_counter % 5 == 0:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            plt.imshow(frame)
            plt.show()
            ideal_left_pupil = gaze.pupil_left_coords()
            ideal_right_pupil = gaze.pupil_right_coords()
            return ideal_left_pupil, ideal_right_pupil

        frame_counter += 1

        if not ret:
            break

    return None, None


def calc_video_focus(url, frame_freq=10, threshold=0, debug=False):

    ideal_left_pupil, ideal_right_pupil = get_ideal_points(url)
    print(f"Ideal Pupil Points: {ideal_left_pupil}, {ideal_right_pupil}")
    if (ideal_left_pupil is None or ideal_right_pupil is None):
        return -1

    cap = cv2.VideoCapture(url)
    focused = []
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and frame_counter % frame_freq == 0:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)
            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            if (left_pupil is None or right_pupil is None):
                return 0
            left_pupil_deviation = calc_pupil_deviation(left_pupil, ideal_left_pupil, frame.shape)
            right_pupil_deviation = calc_pupil_deviation(
                right_pupil, ideal_right_pupil, frame.shape)
            avg_deviaion = (left_pupil_deviation + right_pupil_deviation) / 2

            if (avg_deviaion < threshold):
                focused.append(0)
            else:
                focused.append(1)

            if debug:
                frame = gaze.annotated_frame()
                print(f"==========Frame - {frame_counter}===========")
                print(f"left pupil: {left_pupil}, right pupil: {right_pupil}")
                print(f"Deviation Left: {left_pupil_deviation}, Right: {right_pupil_deviation}")
                print(f"Avg Deviation: {avg_deviaion}")
                cv2.imwrite(f'./images/frame_{frame_counter}_{focused[-1]}.jpg', frame)

        frame_counter += 1

        if not ret:
            break

    focused = np.array(focused)
    return np.sqrt((focused ** 2).mean())


if __name__ == "__main__":
    if not os.path.exists('./images'):
        os.mkdir('images')
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200323_225914.mp4?alt=media&token=da05308f-e165-4297-bd17-5cf5e5d4b818"
    url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200326_200607.mp4?alt=media&token=4d83a2c5-028b-4d7f-a05a-cbdb9cfc11de"
    frame_freq = 10
    threshold = 0.10
    video_focus = calc_video_focus(url, frame_freq, threshold, True)
    print(f"Video focus {video_focus}")
