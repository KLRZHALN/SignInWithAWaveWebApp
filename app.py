from flask import Flask, request, render_template, jsonify, redirect, url_for, session, Response
import sqlite3
import cv2
import threading
from datetime import timedelta
import bcrypt
import  time
from utils.hand_recog import *
from utils.registration import *
from utils.functions import *
from flask_socketio import SocketIO
import time
global camera
redirect_flag = False
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'Freebies#12345'
socketio = SocketIO(app)
face = 0

@app.route("/")
def home():
    return render_template('fakeloginpagehtml.html') 

@app.route("/home")
def home_land():
    session['otp']  = 0
    return render_template('landingpagehtml.html')

@app.route("/about")
def about():
    return render_template('aboutpagehtml.html')

@app.route("/final")
def final():
    return render_template('fakefinalpagehtml.html')

@app.route("/success_page")
def signup():
    session['otp']  = 0
    success_page = render_template('successpagehtml.html')
    def close_app():
        time.sleep(3)
        socketio.emit('time_completed')
        return None
    timer_thread = threading.Thread(target=close_app)
    timer_thread.start()  # Start the timer thread
    return success_page

@app.route("/signin_page", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            res = initialize_database()
            c = res.cursor()
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            account = c.fetchone()
            res.close()

            print("Account:", account)  # Add this line for debugging

            if account is None or not bcrypt.checkpw(password.encode('utf-8'), account[3].encode('utf-8')):
                message = 'Incorrect email or password.'
                return render_template('signinpagehtml.html', msg=message)

            session['email'] = email
            msg, otp = send_otp()
            session['otp'] = otp
            username = account[1]

            # Redirect to the 'buttonpage' route
            return redirect(url_for('buttonpage', username=username))
            return jsonify({'success': True, 'message': 'Sign-in successful', 'username': username}), 200
        except sqlite3.Error as e:
            return jsonify({'message': f'Database error: {str(e)}'}), 500

    return render_template('signinpagehtml.html')
hnd=initialize_recog()

def gen_frames(otp_code):
    with app.app_context(): 
        global camera        
        camera = cv2.VideoCapture(0)      
        gesture = '0'
        if otp_code==0:
            print('empty string')
            socketio.emit('gesture_empty')
        lpst = [int(digit) for digit in str(otp_code)]

        lst = ['', '', '', '']
        start_time = time.time()
        counter=0
        while True:
                success, frame = camera.read()
                if success:                              
                    frame = cv2.flip(frame, 1)
                    frame, new_gesture = detect_hand(hnd, frame)
                    if new_gesture == gesture and gesture != '':
                        elapsed_time = time.time() - start_time
                        if elapsed_time >= 3:
                            if '' in lst:
                                lst[lst.index('')] = gesture
                                start_time = time.time()  # Reset the timer
                    else:
                        gesture = new_gesture
                        start_time = time.time()  # Reset the timer for the new gesture
                    socketio.emit('gesture', gesture)  # Emit gesture data via SocketIO
                else:
                    frame = cv2.flip(frame, 1)
                try:
                    socketio.emit('lst', lst)      
                    # Check if all the integers in the list are filled
                    if all(isinstance(i, int) for i in lst):
                        # Stop the real-time gesture registration
                        time.sleep(2)
                        if lst==lpst :
                            camera.release()
                            lst = ['', '', '', ''] 
                            socketio.emit('gesture_completed')
                        else:
                            counter += 1  # Increment the counter for failed attempts
                            if counter == 3:  # If three failed attempts                                
                                socketio.emit('trail_completed')
                                break                                                              
                            else:
                                socketio.emit('wrong_attempt') 
                                lst = ['', '', '', '']
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'  + b'\r\n')
                except Exception as e:
                    print(f'Error: {str(e)}')
                    continue
                pass

@app.route('/registration', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        db = initialize_database()
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        result, con= registation(username, email, password, db)
        if con==1:
            session['email'] = email
            msg, otp=send_otp()
            session['otp']  = otp
            return result
        else:
            return result        
    return render_template('signuppagehtml.html')

@app.route("/buttonpage")
def buttonpage():
    global camera  # Access the globally declared camera object

    camera = cv2.VideoCapture(0)  # Initialize the camera object if not already initialized

    if camera.isOpened():
        # Release the camera when the button page is accessed
        camera.release()
        camera = None 
    return render_template('menupagehtml.html')

@app.route("/send_otp", methods=['POST', 'GET'])
def sendotp():
    if request.method == 'POST':
        if 'last_otp_time' in session:
            elapsed_time = time.time() - session['last_otp_time']
            if elapsed_time < 60:  # 900 seconds = 15 minutes
                remaining_time = int(60 - elapsed_time)
                msg=jsonify({    "errorType": "customError",
    "errorMessage":  f"Please wait {remaining_time} seconds before requesting another OTP."})

        
        if 'last_otp_time' not in session or elapsed_time >= 60:
            msg, otp = send_otp()  # Calling the send_otp function
            session['otp'] = otp
            session['last_otp_time'] = time.time()
            # socketio.emit("otp_message", msg)  # Emitting 'otp_message' event with the OTP message
        return msg
    return render_template('menupagehtml.html')


@app.route('/camera', methods=['GET'])
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    if session['otp'] is None:
      session['otp']=0000      
    return Response(gen_frames(session['otp'] ), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    otp_code=None
    socketio.start_background_task(target=gen_frames, otp_code=otp_code)
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
