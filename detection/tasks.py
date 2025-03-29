

# from django.apps import apps
# from scipy.spatial import distance as dist
# from imutils.video import VideoStream
# from imutils import face_utils
# from threading import Thread
# import numpy as np
# import argparse
# import imutils
# import time

# import dlib
# import cv2
# import os
# import sys
# import django
# import pygame.mixer


# pygame.mixer.init()


# def play_alarm_sound(sound_file):
#     try:
#         pygame.mixer.music.load(sound_file)
#         pygame.mixer.music.play()
#     except pygame.error as e:
#         print(f"Error playing sound: {e}")


# def alarm(msg):
#     global alarm_status  # drowsiness
#     global alarm_status2  # yawn
#     global saying

#     while alarm_status:
#         play_alarm_sound("detection/static/music.wav")

#     if alarm_status2:

#         saying = True
#         play_alarm_sound("detection/static/music.wav")
#         saying = False


# def eye_aspect_ratio(eye):
#     A = dist.euclidean(eye[1], eye[5])
#     B = dist.euclidean(eye[2], eye[4])

#     C = dist.euclidean(eye[0], eye[3])

#     ear = (A + B) / (2.0 * C)

#     return ear


# def final_ear(shape):
#     # left eye coordinates
#     (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
#     (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

#     leftEye = shape[lStart:lEnd]
#     rightEye = shape[rStart:rEnd]

#     leftEAR = eye_aspect_ratio(leftEye)
#     rightEAR = eye_aspect_ratio(rightEye)

#     ear = (leftEAR + rightEAR) / 2.0
#     return (ear, leftEye, rightEye)


# def lip_distance(shape):
#     top_lip = shape[50:53]
#     top_lip = np.concatenate((top_lip, shape[61:64]))

#     low_lip = shape[56:59]
#     low_lip = np.concatenate((low_lip, shape[65:68]))

#     top_mean = np.mean(top_lip, axis=0)
#     low_mean = np.mean(low_lip, axis=0)

#     distance = abs(top_mean[1] - low_mean[1])
#     return distance


# ap = argparse.ArgumentParser()
# ap.add_argument("-w", "--webcam", type=int, default=0,
#                 help="index of webcam on system")
# args = vars(ap.parse_args())

# EYE_AR_THRESH = 0.2
# EYE_AR_CONSEC_FRAMES = 30  # how many frames to check if the user is sleepy
# YAWN_THRESH = 30  # distance between two lips
# alarm_status = False
# alarm_status2 = False
# saying = False
# COUNTER = 0

# print("-> Loading the predictor and detector...")
# # detector = dlib.get_frontal_face_detector()
# detector = cv2.CascadeClassifier(
#     "detection/static/haarcascade_frontalface_default.xml")
# predictor = dlib.shape_predictor(
#     'detection/static/shape_predictor_68_face_landmarks.dat')


# print("-> Starting Video Stream")
# vs = VideoStream(src=args["webcam"]).start()
# time.sleep(1.0)

# while True:

#     frame = vs.read()
#     frame = imutils.resize(frame, width=550)

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     gray = np.array(gray, dtype=np.uint8)

#     # rects = detector(gray, 0)
#     rects = detector.detectMultiScale(gray, scaleFactor=1.1,
#                                       minNeighbors=5, minSize=(30, 30),
#                                       flags=cv2.CASCADE_SCALE_IMAGE)

#     # for rect in rects:
#     for (x, y, w, h) in rects:
#         rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

#         shape = predictor(gray, rect)
#         shape = face_utils.shape_to_np(shape)

#         eye = final_ear(shape)
#         ear = eye[0]
#         leftEye = eye[1]
#         rightEye = eye[2]

#         distance = lip_distance(shape)

#         leftEyeHull = cv2.convexHull(leftEye)
#         rightEyeHull = cv2.convexHull(rightEye)
#         cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
#         cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

#         lip = shape[48:60]
#         cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

#         if ear < EYE_AR_THRESH:
#             COUNTER += 1

#             if COUNTER >= EYE_AR_CONSEC_FRAMES:
#                 if alarm_status == False:
#                     alarm_status = True
#                     t = Thread(target=alarm, args=('wake up sir',))
#                     t.deamon = True
#                     t.start()

#                 cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

#         else:
#             COUNTER = 0
#             alarm_status = False

#         if (distance > YAWN_THRESH):
#             cv2.putText(frame, "Yawn Alert", (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
#             if alarm_status2 == False and saying == False:
#                 alarm_status2 = True
#                 t = Thread(target=alarm, args=('take some fresh air sir',))
#                 t.deamon = True
#                 t.start()
#         else:
#             alarm_status2 = False

#         cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
#         cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

#     cv2.imshow("Frame", frame)
#     key = cv2.waitKey(1) & 0xFF

#     if key == ord("q"):
#         break

# cv2.destroyAllWindows()
# vs.stop()


import asyncio
import os
import cv2
import dlib
import imutils
import pygame.mixer
from imutils import face_utils
from imutils.video import VideoStream
from scipy.spatial import distance as dist
from .models import Alert, DriverProfile
import numpy as np
from asgiref.sync import sync_to_async
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear


def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)


def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance


async def drowsiness_detection_task(
    webcam_index, ear_thresh, ear_frames, yawn_thresh, driver_profile, driver_email
):
    print("Drowsiness detection task started.")
    alarm_status = False
    alarm_status2 = False
    saying = False
    drowsiness_detected = False

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(
        BASE_DIR, "detection/static/music.wav"))

    print("-> Loading the predictor and detector...")
    detector = cv2.CascadeClassifier(
        "detection/static/haarcascade_frontalface_default.xml")
    predictor = dlib.shape_predictor(
        "detection/static/shape_predictor_68_face_landmarks.dat")

    print("-> Starting Video Stream")
    try:
        vs = VideoStream(src=webcam_index).start()
        print("Video stream opened successfully.")
    except Exception as e:
        print(f"Error opening video stream: {e}")
        return  # Exit the function if the video stream cannot be opened

    await asyncio.sleep(1.0)  # Allow the video stream to warm up

    COUNTER = 0

    while True:
        frame = vs.read()
        if frame is None:
            print("Error: No video frame received.")
            break

        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        for x, y, w, h in rects:
            rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            eye = final_ear(shape)
            ear = eye[0]
            leftEye = eye[1]
            rightEye = eye[2]

            distance = lip_distance(shape)

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            lip = shape[48:60]
            cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

            if ear < ear_thresh:
                COUNTER += 1

                if COUNTER >= ear_frames:
                    if not drowsiness_detected:
                        drowsiness_detected = True
                        msg = "Drowsiness detected!"
                        print("Playing audio alert...")
                        pygame.mixer.music.play()
                        print("call")
                        # s = 'espeak "' + msg + '"'
                        # await sync_to_async(os.system)(s)

                        alert = Alert(
                            driver=driver_profile,
                            alert_type="drowsiness",
                            description=msg,
                        )
                        await sync_to_async(alert.save, thread_sensitive=True)()

                        if alert.alert_type == "drowsiness":
                            subject = "Drowsiness Alert"
                            email_template = "drowsiness_alert.html"
                            context = {
                                "driver": driver_profile,
                                "alert": alert,
                                "driver_first_name": driver_profile.user.first_name,
                            }
                            message = render_to_string(email_template, context)
                            email = EmailMessage(
                                subject, message, to=[driver_email])
                            email.content_subtype = "html"
                            email.send()

                    cv2.putText(
                        frame,
                        "DROWSINESS ALERT!",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )
            else:
                COUNTER = 0
                drowsiness_detected = False

            if distance > yawn_thresh:
                msg = "Yawn Alert"
                if not alarm_status2 and not saying:
                    alarm_status2 = True
                    print("Playing audio alert...")
                    pygame.mixer.music.play()
                    print("call")
                    saying = True
                    # s = 'espeak "' + msg + '"'
                    # await sync_to_async(os.system)(s)
                    saying = False
                    alarm_status2 = False  # Reset the alarm_status2 flag

                    alert = Alert(
                        driver=driver_profile, alert_type="yawning", description=msg
                    )
                    await sync_to_async(alert.save, thread_sensitive=True)()

                cv2.putText(
                    frame,
                    "Yawn Alert",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
            else:
                alarm_status2 = False

            cv2.putText(
                frame,
                "EAR: {:.2f}".format(ear),
                (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                "YAWN: {:.2f}".format(distance),
                (300, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        await asyncio.sleep(0)  # Allow the async context to switch

    cv2.destroyAllWindows()
    vs.stop()
    print("Drowsiness detection task completed.")
