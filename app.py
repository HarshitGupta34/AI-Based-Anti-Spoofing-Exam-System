import math
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, session,redirect,url_for,Response,flash
import os
from flask_mysqldb import MySQL
import json
import io
import numpy as np
from enum import Enum
import warnings
import threading
import utils
import random
import time
import cv2
import keyboard
from dotenv import load_dotenv
import os

load_dotenv()
#variables
studentInfo=None
camera=None
profileName=None

#Flak's Application Confguration
warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'xyz'
# app.config["MONGO_URI"] = "mongodb://localhost:27017/"
os.path.dirname("../templates")

#Flak's Database Configuration
app.secret_key = os.getenv("SECRET_KEY")

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
mysql = MySQL(app)

executor = ThreadPoolExecutor(max_workers=4)  # Adjust the number of workers as needed
def capture_by_frames():

    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:

        success, frame = utils.cap.read()

        if not success or frame is None:
            continue

        detector = cv2.CascadeClassifier(
            'Haarcascades/haarcascade_frontalface_default.xml'
        )

        faces = detector.detectMultiScale(frame, 1.2, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#Function to run Cheat Detection when we start run the Application


#Login Related
@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global studentInfo
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, email, password, role FROM students WHERE Email=%s AND Password=%s", (username, password))
        data = cur.fetchone()
        if data is None:
            flash('Your Email or Password is incorrect, try again.', category='error')
            return redirect(url_for('main'))
        else:
            id, name, email, password, role = data
            studentInfo = {"Id": id, "Name": name, "Email": email, "Password": password}

    # check exam status
            cur.execute("SELECT exam_status FROM students WHERE Email=%s", (email,))
            exam_status = cur.fetchone()[0]

            if role.lower() == 'student':
                utils.Student_Name = name

                if exam_status == 'given':
                    flash('You already gave the exam', 'error')
                    return redirect(url_for('main'))
                else:
                    return redirect(url_for('rules'))
            else:
                return redirect(url_for('adminStudents'))

@app.route('/logout')
def logout():
    return render_template('login.html')

#Student Related
@app.route('/rules')
def rules():
    return render_template('ExamRules.html')

@app.route('/faceInput')
def faceInput():
    return render_template('ExamFaceInput.html')

@app.route('/video_capture')
def video_capture():
    return Response(capture_by_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/saveFaceInput')
def saveFaceInput():
    global profileName
    if utils.cap.isOpened():
        utils.cap.release()
    cam = cv2.VideoCapture(0)
    success, frame = cam.read()  # read the camera frame
    profileName=f"{studentInfo['Name']}_{utils.get_resultId():03}" + "Profile.jpg"
    cv2.imwrite(profileName,frame)
    utils.move_file_to_output_folder(profileName,'Profiles')
    cam.release()
    return redirect(url_for('confirmFaceInput'))

@app.route('/confirmFaceInput')
def confirmFaceInput():
    profile = profileName
    utils.fr.encode_faces()
    return render_template('ExamConfirmFaceInput.html', profile = profile)

@app.route('/systemCheck')
def systemCheck():
    return render_template('ExamSystemCheck.html')

@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    if request.method == 'POST':
        examData = request.json
        output = 'exam'
        if 'Not available' in examData['input'].split(';'): output = 'systemCheckError'
    return jsonify({"output": output})

@app.route('/systemCheckError')
def systemCheckError():
    return render_template('ExamSystemCheckError.html')

@app.route('/exam')
def exam():
    utils.Globalflag = True
    utils.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

   # threading.Thread(target=utils.cheat_Detection1).start()
    threading.Thread(target=utils.cheat_Detection2).start()
    threading.Thread(target=utils.fr.run_recognition).start()
    threading.Thread(target=utils.a.record).start()

    keyboard.hook(utils.shortcut_handler)

    return render_template('Exam.html')

@app.route('/exam', methods=["POST"])
def examAction():
    link = ''
    if request.method == 'POST':
        examData = request.json
        if(examData['input']!=''):
            utils.Globalflag= False
            utils.cap.release()
            utils.write_json({
                "Name": ('Prohibited Shorcuts (' + ','.join(list(dict.fromkeys(utils.shorcuts))) + ') are detected.'),
                "Time": (str(len(utils.shorcuts)) + " Counts"),
                "Duration": '',
                "Mark": (1.5 * len(utils.shorcuts)),
                "Link": '',
                "RId": utils.get_resultId()
            })
            utils.shorcuts=[]
            trustScore= utils.get_TrustScore(utils.get_resultId())
            totalMark=  math.floor(float(examData['input'])* 6.6667)
            if trustScore >=30:
                status="Fail(Cheating)"
                link = 'showResultFail'
            else:
                if totalMark < 50:
                    status="Fail"
                    link = 'showResultFail'
                else:
                    status="Pass"
                    link = 'showResultPass'
            utils.write_json({
                "Id": utils.get_resultId(),
                "Name": studentInfo['Name'],
                "TotalMark": totalMark,
                "TrustScore": max(100-trustScore, 0),
                "Status": status,
                "Date": time.strftime("%Y-%m-%d", time.localtime(time.time())),
                "StId": studentInfo['Id'],
                "Link" : profileName
            },"result.json")
            cur = mysql.connection.cursor()
            cur.execute("UPDATE students SET exam_status='given' WHERE Email=%s", (studentInfo['Email'],))
            mysql.connection.commit()
            resultStatus= studentInfo['Name']+';'+str(totalMark)+';'+status+';'+time.strftime("%Y-%m-%d", time.localtime(time.time()))
        else:
            utils.Globalflag = True
            resultStatus=''
    return jsonify({"output": resultStatus, "link": link})

@app.route('/showResultPass/<result_status>')
def showResultPass(result_status):
    return render_template('ExamResultPass.html',result_status=result_status)

@app.route('/showResultFail/<result_status>')
def showResultFail(result_status):
    return render_template('ExamResultFail.html',result_status=result_status)

#Admin Related
@app.route('/adminResults')
def adminResults():
    results = utils.getResults()
    return render_template('Results.html', results=results)

@app.route('/adminResultDetails/<resultId>')
def adminResultDetails(resultId):
    result_Details = utils.getResultDetails(resultId)
    return render_template('ResultDetails.html', resultDetials=result_Details)

@app.route('/adminResultDetailsVideo/<videoInfo>')
def adminResultDetailsVideo(videoInfo):

    videoInfo = videoInfo.split(';')

    filename = videoInfo[0]
    resultId = videoInfo[1]

    # AUDIO
    if filename.endswith('.wav'):

        mediaPath = '/static/OutputAudios/' + filename

    # VIDEO
    else:

        mediaPath = '/static/OutputVideos/' + filename

    return render_template(
        'ResultDetailsVideo.html',
        mediaPath=mediaPath,
        filename=filename,
        resultId=resultId
    )
@app.route('/adminStudents')
def adminStudents():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students where Role='STUDENT'")
    data = cur.fetchall()
    cur.close()
    return render_template('Students.html', students=data)

@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    if request.method == "POST":
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (Name, Email, Password, Role) VALUES (%s, %s, %s, %s)", (name, email, password,'STUDENT'))
        mysql.connection.commit()
        return redirect(url_for('adminStudents'))

@app.route('/deleteStudent/<string:stdId>', methods=['GET'])
def deleteStudent(stdId):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE ID=%s", (stdId,))
    mysql.connection.commit()
    return redirect(url_for('adminStudents'))

@app.route('/updateStudent', methods=['POST', 'GET'])
def updateStudent():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE students
               SET Name=%s, Email=%s, Password=%s
               WHERE ID=%s
            """, (name, email, password, id_data))
        mysql.connection.commit()
        return redirect(url_for('adminStudents'))

if __name__ == '__main__':
    app.run(debug=True)