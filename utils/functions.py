import cv2
import copy
import itertools
import numpy as np
import sqlite3
from flask import Flask, request, jsonify, session
import sqlite3
import re
import random
from email.mime.application import MIMEApplication
import smtplib
import cv2
from utils.hand_recog import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def initialize_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
                )''')
    conn.commit()
    return conn
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point = [np.array((landmark_x, landmark_y))]
        landmark_array = np.append(landmark_array, landmark_point, axis=0)
    x, y, w, h = cv2.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])
    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]
        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))
    max_value = max(list(map(abs, temp_landmark_list)))
    def normalize_(n):
        return n / max_value
    temp_landmark_list = list(map(normalize_, temp_landmark_list))
    return temp_landmark_list


def send_otp():
    if 'email' in session:
        # Get the email from the session data
        email = session.get('email')

        # Generate OTP
        otp = str(random.randint(1000, 9999))

        # Send OTP to user's email
        sender_email = 'signwithawave@gmail.com'
        sender_password = 'pnqqiaxejsrafpwm'
        subject = 'Sign-in With A Wave: OTP Verification Code'
        message =  f"Your OTP Code is: <b>{otp}</b>\n\n" \
              f"- We appreciate you utilizing the 'sign in with a wave' feature.\n" \
              f"- The PDF attachment includes every hand sign from 0 to 9 needed to complete the OTP code.\n\n"\
              f"Regarding the OTP Instructions:\n "\
              f"""1. Go to "Open the Camera".\n """\
              f"2. Provide the OTP Code using the appropriate Numbered Gesture in the gesture.pdf File.\n "\
              f"""3. You are able to resend a new OTP Code every 1 minute. If you have exhausted three wrong attempts, kindly "Resend OTP".\n """\
              f"4. If you are redirected to your original webpage, you have successfully signed in!\n\n "\
              f"Thank you for using Sign With A Wave."
        try:
            # Create a multipart message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject

            # Add the text message to the email
            msg.attach(MIMEText(f"""\
Your OTP Code is: <b>{otp}</b><br><br>
* We appreciate you utilizing the 'sign in with a wave' feature.<br><br>

* The PDF attachment includes every hand sign from 0 to 9 needed to complete the OTP code.<br><br>

Regarding the OTP Instructions:<br><br>
1. Go to "Open the Camera".<br>

2. Provide the OTP Code using the appropriate Numbered Gesture in the gesture.pdf File.<br>

3. You are able to resend a new OTP Code every 1 minute. If you have exhausted three wrong attempts, kindly "Resend OTP".<br>

4. If you are redirected to your original webpage, you have successfully signed in!<br><br>

Please get in touch with us at:<br>
Phone number: +966-58-226-6073 <br>
Email: signwithawave@gmail.com<br><br>


Thank you for using Sign With A Wave.
""", "html"))

            # Attach the PDF file
            pdf_attachment_path = 'files/gestures.pdf'
            with open(pdf_attachment_path, 'rb') as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), 'pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename='gestures.pdf')
                msg.attach(pdf_attachment)

            # Set up the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            # Log in to the email account
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, email, msg.as_string())

            # Quit the server
            server.quit()

            # Return success response with status and message
            return jsonify({"success": True}), otp
        except Exception as e:
            # Handle email sending error and return failure response
            print(e)
            return jsonify({"success": False}), otp
    else:
        # Handle case where email is not found in session (user not logged in)
        return jsonify({"success": False}), otp