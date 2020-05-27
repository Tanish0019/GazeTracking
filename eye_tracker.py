import os
import shutil
import cv2
import numpy as np
from gaze_tracking import GazeTracking

gaze = GazeTracking()
ideal_points_dict = {}


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
    ideal_frame_max = 30
    cap = cv2.VideoCapture(url)
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if ret and frame_counter % 10 == 0 and frame_counter <= ideal_frame_max:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)

            if debug:
                frame = gaze.annotated_frame()
                cv2.imwrite('./images/ideal_frame.jpg', frame)

            if not gaze.is_center():
                frame_counter += 1
                continue

            ideal_left_pupil = gaze.pupil_left_coords()
            ideal_right_pupil = gaze.pupil_right_coords()
            normal_x = gaze.x_cords()
            normal_y = gaze.y_cords()
            if None in [ideal_left_pupil, ideal_right_pupil, normal_x, normal_y]:
                frame_counter += 1
                continue

            ideal_normal_left = (normal_x[0], normal_y[0])
            ideal_normal_right = (normal_x[1], normal_y[1])
            return ideal_left_pupil, ideal_right_pupil, ideal_normal_left, ideal_normal_right

        frame_counter += 1

        if frame_counter > ideal_frame_max:
            return -1

        if not ret:
            break

    return -1


def calc_video_focus(url, threshold=0.071, video_id="dummy_id", debug=False):
    if video_id in ideal_points_dict:
        ideal_points = ideal_points_dict[video_id]
        print("points already exists:", ideal_points)
    else:
        ideal_points = get_ideal_points(url, debug)
        ideal_points_dict[video_id] = ideal_points
        print("points don't exist. New points:", ideal_points)

    if ideal_points == -1:
        return (-1,0)

    ideal_left_pupil, ideal_right_pupil, ideal_normal_left, ideal_normal_right = ideal_points

    print(f"Ideal Pupil Points: {ideal_left_pupil}, {ideal_right_pupil}")
    print(f"Ideal Normalized Points: {ideal_normal_left}, {ideal_normal_right}")

    cap = cv2.VideoCapture(url)

    # check video after every 0.5seconds
    fps = int(np.ceil(cap.get(cv2.CAP_PROP_FPS)))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    frame_freq = fps // 2
    print(f"fps: {fps}, frame_freq: {frame_freq}")
    focused = []
    frame_counter = 1
    while cap.isOpened():
        ret, frame = cap.read()

        if ret and frame_counter % frame_freq == 0:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gaze.refresh(frame)

            if gaze.check_blink():
                if debug:
                    print(f"==========Frame - {frame_counter}===========")
                    print("GAZE Blink")
                    cv2.imwrite(f'./images/f_{frame_counter}_BLINK.jpg', frame)
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
            exit = 0
            if (avg_deviaion < threshold):
                focused.append(1)
            else:
                print(f'deviation: {avg_deviaion} frame count: ',frame_counter)
                exit = 1
                focused.append(0)

            if debug:
                frame = gaze.annotated_frame()
                print(f"==========Frame - {frame_counter}===========")
                print(f"left pupil: {left_pupil}, right pupil: {right_pupil}")
                print(f"Ideal Pupil Points: {ideal_left_pupil}, {ideal_right_pupil}")
                print(f"Deviation Left: {left_pupil_deviation}, Right: {right_pupil_deviation}")
                print(f"Avg Deviation: {avg_deviaion}")
                cv2.imwrite(f'./images/f_{frame_counter}_{focused[-1]}.jpg', frame)
            if(exit):
                return (frame_counter//frame_freq,np.ceil(duration))
        frame_counter += 1

        if not ret:
            break

    # focused = np.array(focused)
    # correct = focused.sum()
    # incorrect = len(focused) - correct
    # mean = focused.mean()
    # print(f"Number of Frame:{len(focused)}, correct: {correct}, Incorrect: {incorrect}")
    # print(f"url: {url}")
    # print(f"mean: {mean}")
    print('frame count: ',frame_counter)
    return (frame_counter//frame_freq,np.ceil(duration))


if __name__ == "__main__":
    if os.path.exists('./images'):
        shutil.rmtree('./images')
    os.mkdir('images')

    # Tanish
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200326_200607.mp4?alt=media&token=4d83a2c5-028b-4d7f-a05a-cbdb9cfc11de"
    # Shivam 1
    url1 = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_001923.mp4?alt=media&token=80f105e3-540a-4086-a84b-241d0b8db7de"
    # Shivam 2
    url2 = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002111.mp4?alt=media&token=8c9a2126-40b6-4bee-8bd2-a6d189a7e629"
    # Shivam 3
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_110252.mp4?alt=media&token=1f04063d-4d90-43d4-aef9-e1c5a2d13762"
    # Utkarsh
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002341.mp4?alt=media&token=e522faca-f700-4f82-83d4-401f67945817"
    # Deep
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002627.mp4?alt=media&token=2568434e-ab28-4f02-a9cc-55d5515e2985"
    # Aheli
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_002745.mp4?alt=media&token=f216032b-1d08-4445-9858-bda358f1fba9"

    # Test cases:
    # 100%  Getting 95%
    # Problem: Blinking frames are reducing accuracy
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_161141.mp4?alt=media&token=602cedfc-b33f-47ec-a287-6c1e60b54ed2"
    # 55% BUT 68%
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_135416.mp4?alt=media&token=2ce4e983-a47d-479d-9815-2486604f42fa"
    # 20% BUT 42%
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_135637.mp4?alt=media&token=f1e0c98c-1c48-43d9-9102-f9134c8d6df5"
    # 0% BUT 30%
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_140642.mp4?alt=media&token=a91bc5ae-8216-4f31-bac4-ea919e1711ff"
    # 0 but 16%
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_141655.mp4?alt=media&token=3c3699a8-4705-4562-ac8d-0c029e94fa1b"
    # 0 but 19%
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_141452.mp4?alt=media&token=5593d820-c0e7-4620-8e9d-d68299ac9eaa"
    # 0 but 19
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200403_141904.mp4?alt=media&token=c485a05b-fad6-43c8-9754-4325e0f5e98d"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200406_163640.mp4?alt=media&token=edb0b858-627a-4afc-987c-8927146f0ec9"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200406_172628.mp4?alt=media&token=6c8bebec-a9fb-4c8a-9249-b940d8a13d0a"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200406_172526.mp4?alt=media&token=63e4021f-bd10-4133-86d0-aa5b92384a7a"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200407_194735.mp4?alt=media&token=d8d88a6b-1e82-484f-a350-71ca1dcc145c"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200407_214400.mp4?alt=media&token=6f642531-aee6-4821-ac67-91b6fb57e25e"
    url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200409_162045.mp4?alt=media&token=cb8a4b5b-5056-493f-b099-c5dacf397f6b"
    url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_20200413_162234.mp4?alt=media&token=dab2c5a2-38ba-48e2-95e7-54a43ce460e1"
    url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1587112714281.mp4?alt=media&token=0bf861b4-5850-4e7a-8849-4c76b3e2a3da"
    # url = "https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1587124049503.mp4?alt=media&token=0e77d104-18e6-485e-b763-92944f08de27"
    threshold = 0.071
    url = 'https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1589462033162.mp4?alt=media&token=97139771-2e52-4388-8e48-5786594b6844'
    url = 'https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1589550852617.mp4?alt=media&token=690d82aa-8865-40c2-bb1a-b84cabc04bd8'
    url = 'https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images/VID_1590216612025.mp4?alt=media&token=63b8e2ab-c510-4c68-a1d4-f8c67ef17367'
    url = 'https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1590557238195.mp4?alt=media&token=948f916c-989b-466d-8948-a09ba6fdd7c1'
    url = 'https://firebasestorage.googleapis.com/v0/b/mcandlefocus.appspot.com/o/images%2FVID_1590557025259.mp4?alt=media&token=7703a513-9e8a-4493-99ef-ca16619e86d5'
    video_focus = calc_video_focus(url=url, threshold=threshold, video_id="video_id", debug=True)
    print(f"Video focus {video_focus}")
    # print(ideal_points_dict)
    # video_focus = calc_video_focus(
    #     url=url1,
    #     frame_freq=frame_freq,
    #     threshold=threshold,
    #     video_id="video_id",
    #     debug=False)
    print(f"Video focus {video_focus}")
