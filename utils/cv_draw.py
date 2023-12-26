import cv2 as cv
keypoint_classifier_labels = [0,1,2,3,4,5,6,7,8,9 ]
def draw_landmarks(image, landmark_point):
    lines = [
        (2, 3), (3, 4),  # Thumb
        (5, 6), (6, 7), (7, 8),  # Index finger
        (9, 10), (10, 11), (11, 12),  # Middle finger
        (13, 14), (14, 15), (15, 16),  # Ring finger
        (17, 18), (18, 19), (19, 20),  # Little finger
        (0, 1), (1, 2), (2, 5), (5, 9),  # Palm
        (9, 13), (13, 17), (17, 0)
    ]
    # Draw lines
    for start, end in lines:
        cv.line(image, tuple(landmark_point[start]), tuple(landmark_point[end]), (255, 255, 255), 2)
    # Draw circles
    for index, landmark in enumerate(landmark_point):
        if index in {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 8, 12, 16, 20}:
            cv.circle(image, tuple(landmark), 5, (210, 180, 140), -1)  # Light brown color
            cv.circle(image, tuple(landmark), 5, (0, 0, 0), 1)  # Black border
    return image


def draw_info_text(image, brect, handedness,  hand_sign_id, conf):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 32),
                 (255, 0,0), -1)

    info_text = handedness.classification[0].label[0:]
    if conf is not None and hand_sign_id is not None:
        info_text = hand_sign_id
    else:
        info_text = " Unknown Gesture"

    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255, 255), 1, cv.LINE_AA)
    return image