import os
import shutil
import cv2
import numpy as np
from gaze_tracking import GazeTracking
import matplotlib.pyplot as plt

gaze = GazeTracking()


def calc_pupil_deviation(pupil_coords, ideal_coords, frame_dimensions=None):
    if frame_dimensions:
        x1 = ideal_coords[0] / frame_dimensions[0]
        x2 = pupil_coords[0] / frame_dimensions[0]
        y1 = ideal_coords[1] / frame_dimensions[1]
        y2 = pupil_coords[1] / frame_dimensions[1]
    else:
        x1, x2, y1, y2 = pupil_coords[0], ideal_coords[0], pupil_coords[1], ideal_coords[1]
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_ideal_points(url, debug=False):
    cap = cv2.VideoCapture(url)
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and frame_counter % 10 == 0:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)

            if not gaze.is_center():
                return None

            if debug:
                frame = gaze.annotated_frame()
                plt.imshow(frame)
                plt.show()

            ideal_left_pupil = gaze.pupil_left_coords()
            ideal_right_pupil = gaze.pupil_right_coords()
            normal_x = gaze.x_cords()
            normal_y = gaze.y_cords()
            if None in [ideal_left_pupil, ideal_right_pupil, normal_x, normal_y]:
                return None

            ideal_normal_left = (normal_x[0], normal_y[0])
            ideal_normal_right = (normal_x[1], normal_y[1])
            return ideal_left_pupil, ideal_right_pupil, ideal_normal_left, ideal_normal_right

        frame_counter += 1

        if not ret:
            break

    return None


def calc_video_focus(url, frame_freq=10, threshold=0, debug=False):
    ideal_points = get_ideal_points(url, debug)
    if ideal_points is None:
        return -1
    ideal_left_pupil, ideal_right_pupil, ideal_normal_left, ideal_normal_right = ideal_points
    print(f"Ideal Pupil Points: {ideal_left_pupil}, {ideal_right_pupil}")
    print(f"Ideal Normalized Points: {ideal_normal_left}, {ideal_normal_right}")
    cap = cv2.VideoCapture(url)
    focused = []
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and frame_counter % frame_freq == 0:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)

            if not gaze.is_center():
                focused.append(0)
                if debug:
                    print(f"==========Frame - {frame_counter}===========")
                    print("GAZE NOT CENTER")
                    cv2.imwrite(f'./images/f_{frame_counter}_NOT_CENTER.jpg', frame)
                frame_counter += 1
                continue

            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()
            normal_x = gaze.x_cords()
            normal_y = gaze.y_cords()

            if None in [left_pupil, right_pupil, normal_x, normal_y]:
                focused.append(0)
                if debug:
                    print(f"==========Frame - {frame_counter}===========")
                    print("COORDINATES NONE")
                    cv2.imwrite(f'./images/f_{frame_counter}_NOT_FOUND.jpg', frame)
                frame_counter += 1
                continue

            normal_left = (normal_x[0], normal_y[0])
            normal_right = (normal_x[1], normal_y[1])
            left_pupil_deviation = calc_pupil_deviation(normal_left, ideal_normal_left)
            right_pupil_deviation = calc_pupil_deviation(
                normal_right, ideal_normal_right)
            avg_deviaion = (left_pupil_deviation + right_pupil_deviation) / 2

            if (avg_deviaion < threshold):
                focused.append(1)
            else:
                focused.append(0)

            if debug:
                frame = gaze.annotated_frame()
                print(f"==========Frame - {frame_counter}===========")
                print(f"left pupil: {left_pupil}, right pupil: {right_pupil}")
                print(f"Ideal Pupil Points: {ideal_left_pupil}, {ideal_right_pupil}")
                print(f"Deviation Left: {left_pupil_deviation}, Right: {right_pupil_deviation}")
                print(f"Avg Deviation: {avg_deviaion}")
                cv2.imwrite(f'./images/f_{frame_counter}_{focused[-1]}.jpg', frame)

        frame_counter += 1

        if not ret:
            break

    focused = np.array(focused)
    return np.sqrt((focused ** 2).mean())


if __name__ == "__main__":
    if os.path.exists('./images'):
        shutil.rmtree('./images')
    os.mkdir('images')

    # Tanish
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200326_200607.mp4?alt=media&token=4d83a2c5-028b-4d7f-a05a-cbdb9cfc11de"
    # Shivam 1
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_001923.mp4?alt=media&token=80f105e3-540a-4086-a84b-241d0b8db7de"
    # Shivam 2
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002111.mp4?alt=media&token=8c9a2126-40b6-4bee-8bd2-a6d189a7e629"
    # Utkarsh
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002341.mp4?alt=media&token=e522faca-f700-4f82-83d4-401f67945817"
    # Deep
    url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002627.mp4?alt=media&token=2568434e-ab28-4f02-a9cc-55d5515e2985"
    # Aheli
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002745.mp4?alt=media&token=f216032b-1d08-4445-9858-bda358f1fba9"

    frame_freq = 10
    threshold = 0.07
    video_focus = calc_video_focus(url, frame_freq, threshold, True)
    print(f"Video focus {video_focus}")
