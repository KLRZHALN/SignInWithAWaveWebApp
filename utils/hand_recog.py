import cv2
from utils.cv_draw import draw_landmarks, draw_info_text
from utils.keypoint_classifier import gesture_classification
from utils.functions import *
import mediapipe as mp
import copy

def initialize_recog():
    use_static_image_mode = False
    min_detection_confidence = 0.7
    min_tracking_confidence = 0.5
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence, 
        )
    return hands
def detect_hand(hands, image):
    debug_image = copy.deepcopy(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    tipIds = [4, 8, 12, 16, 20]
    image.flags.writeable = True

    # Assume no hands are detected initially
    no_hand_detected = True

    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            if handedness.classification[0].label == "Right":
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)
                if len(landmark_list) != 0:
                        fingers = []

                        # Thumb
                        if landmark_list[tipIds[0]] > landmark_list[tipIds[0] - 1]:
                            fingers.append(0)
                        else:
                            fingers.append(1)

                        # 4 Fingers
                        for id in range(1, 5):
                            if landmark_list[tipIds[id]][1] < landmark_list[tipIds[id] - 2][1]:
                                fingers.append(1)
                            else:
                                fingers.append(0)

                gesture=gesture_classification(fingers)
                debug_image = draw_landmarks(debug_image, landmark_list)
                # debug_image = draw_info_text(debug_image, brect, handedness, gesture, conf='')
                no_hand_detected = False
                break  # Exit the loop after processing the first right hand

    # If no right hand is detected, return the original image
    if no_hand_detected:
        debug_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        gesture=''
    
    return debug_image, gesture

