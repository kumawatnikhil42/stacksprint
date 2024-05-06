from flask import Flask,render_template,request, redirect, url_for,Response,session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from PIL import Image
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import cv2
import mediapipe as mp
import numpy as np
import os
from werkzeug.utils import secure_filename
# spreadsheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials= ServiceAccountCredentials.from_json_keyfile_name('cred.json',scope)

client = gspread.authorize(credentials)
sheet = client.open("Register Sheet").sheet1
data = sheet.get_all_records()

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def send_email(to_email,attachment_path):
    subject="Successful Registration"
    body="Thank you for registering. Please find your QR code attached below."
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = "trendtrove31@gmail.com"
    msg["To"] = to_email
    msg.attach(MIMEText(body, 'plain'))
    
    
    attachment = open(attachment_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path)
    msg.attach(part)

    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("trendtrove31@gmail.com", "ejyj jexe genk ovud")
        server.sendmail("trendtrove31@gmail.com", to_email, msg.as_string())
        server.quit()
UPLOAD_FOLDER = 'static/uploads'

# Specify the allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'
app.secret_key = 'attendancesystemkey'
logged_in_user = None
name_user=None

@app.route("/")
def home():
 
   
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/submit', methods=['POST'])
def submit():
    global name_user
    global logged_in_user
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        data = sheet.get_all_records()
        name_exists = any(row['Name'] == name for row in data)
        email_exists = any(row['Email'] == email for row in data)
        password_exists = any(row['Password'] == password for row in data)

        if not name_exists:
            return "Enter Registered Name"
        elif not email_exists:
            return "<h1>Enter Registered Email</h1>"
        elif not password_exists:
            return "<h1>Enter Registered Password</h1>"
        else:
            session['name_user'] = name
            session['logged_in_user'] = email
            return redirect(url_for('home'))

allowed_wifi_ip ="127.0.0.1"
@app.route('/info')
def info():
    global logged_in_user
    if session.get('logged_in_user') :
        user_ip = request.remote_addr

        if user_ip != allowed_wifi_ip:
            return "<h1>You are not connected to the allowed WiFi network.</h1>"

        return render_template('attendence.html')
    else:
        return redirect(url_for('login'))
@app.route('/process_qr_code', methods=['POST'])
def process_qr_code():
    global logged_in_user
    if request.method == 'POST':

        content = request.json.get('content')
        

        content_parts = content.split(',')


        name = content_parts[0].strip()
        email = content_parts[1].strip()
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        for row in data:
            if any(row['Email'] == email for row in sheet.get_all_records()):
                newsheet = client.open("Attendance Sheet").sheet1
                newsheet.append_row([name, email,current_date,current_time])
       
                return '<h1>Scan Successfull</h1>'
            else:
                return "<h1>You are not Registered</h1>"




@app.route("/register")
def register():
    return render_template("registration.html")


@app.route('/send', methods=['POST'])
def send():
    global logged_in_user
   
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['confirm_password']

        if any(row['Email'] == email for row in sheet.get_all_records()):
            return "This Email is already registered"
        else:
            if password == c_password:
                filename = f"static/image/{email}.png"
                generate_qr_code(f"{name},{email}", filename)

                current_date = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M:%S")
                sheet.append_row([name, email, password,current_date, current_time])
                send_email(email, filename)
                return redirect(url_for('login'))
            else:
                return "<h1>Password and Confirm Password do not match</h1>"

@app.route('/test')
def test():
     global logged_in_user
     if session.get('logged_in_user'):
        return render_template("test.html")
     else:
        return redirect(url_for('login'))

@app.route('/python')
def python():
    global logged_in_user
    if session.get('logged_in_user'):
        return render_template("python.html")
    else:
        return redirect(url_for('login'))

@app.route('/ml')
def ml():
    global logged_in_user
    if session.get('logged_in_user'):
        return render_template("ml.html")
    else:
        return redirect(url_for('login'))

@app.route('/dl')
def dl():
    global logged_in_user
    if session.get('logged_in_user'):
        return render_template("dl.html")
    else:
        return redirect(url_for('login'))
    
@app.route('/powerbi')
def powerbi():
    global logged_in_user
    if session.get('logged_in_user'):
        return render_template("powerbi.html")
    else:
        return redirect(url_for('login'))
    
@app.route('/excel')
def excel():
    global logged_in_user
    if session.get('logged_in_user'):
        return render_template("excel.html")
    else:
        return redirect(url_for('login'))

def looking():
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5)
    FACE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (5, 6), (6, 7), (7, 8),
    (9, 10), (10, 11), (11, 12),
    (13, 14), (14, 15), (15, 16),
    (17, 18), (18, 19), (19, 20),
    (21, 22), (22, 23), (23, 24),
    (25, 26), (26, 27), (27, 28),
    (29, 30), (30, 31), (31, 32),
    (33, 34), (34, 35), (35, 36),
    (37, 38), (38, 39), (39, 40),
    (41, 42), (42, 43), (43, 44),
    (45, 46), (46, 47), (47, 48),
    (49, 50), (50, 51), (51, 52),
    (53, 54), (54, 55), (55, 56),
    (57, 58), (58, 59), (59, 48),
    (60, 61), (61, 62), (62, 63),
    (64, 65), (65, 66), (66, 67),
    (68, 69), (69, 70), (70, 71),
    (72, 73), (73, 74), (74, 75),
    (76, 77), (77, 78), (78, 79),
    (80, 81), (81, 82), (82, 83),
    (84, 85), (85, 86), (86, 87),
    (88, 89), (89, 90), (90, 91)
]

    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()

            if not success:
                print("Error reading frame")
                break

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = face_mesh.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            img_height, img_width, _ = image.shape
            face_3d = []
            face_2d = []

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx in [33, 263, 1, 61, 291, 199]:
                            if idx == 1:
                                nose_2d = (lm.x * img_width, lm.y * img_height)
                                nose_3d = (lm.x * img_width, lm.y * img_height, lm.z * 3000)
                            x, y = int(lm.x * img_width), int(lm.y * img_height)

                            face_2d.append([x, y])
                            face_3d.append([x, y, lm.z])

                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    focal_length = 1 * img_width
                    cam_matrix = np.array([[focal_length, 0, img_width / 2],
                                       [0, focal_length, img_height / 2],
                                       [0, 0, 1]])

                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                    rmat, jac = cv2.Rodrigues(rot_vec)
                    angles, mtxr, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    x = angles[0] * 360
                    y = angles[1] * 360
                    z = angles[2] * 360

                    if y < -10:
                        return "Looking Left"
                    elif y > 10:
                        return "Looking Right"
                    elif x > 10:
                        text = "Looking Up"
                    else:
                        text = "Forward"

                    cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

#             mp_drawing.draw_landmarks(
#                 image=image,
#                 landmark_list=face_landmarks,
#                 connections=FACE_CONNECTIONS,
#                 landmark_drawing_spec=drawing_spec,
#                 connection_drawing_spec=drawing_spec)
            cv2.imshow('Head Pose Estimation', image)
        
            # if text in ["Looking Left","Looking Right"]:
            #     break
            if cv2.waitKey(5) & 0xFF == 27:
                break 

    cap.release()
    cv2.destroyAllWindows()

@app.route("/startcam")
def startcam():
    global logged_in_user
    if session.get('logged_in_user'):
            return redirect(url_for('test', camera_status=looking()))
    else:
        return redirect(url_for('login'))
    
@app.route("/logout")
def logout():
    global logged_in_user
    
    session.pop('logged_in_user', None) # Clear the session variable
    return redirect(url_for('login'))

quizsheet= client.open("Register Sheet").get_worksheet(1)


@app.route("/quiz")
def quiz():
    global logged_in_user
    global name_user
    if session.get('logged_in_user'):
        named_data=quizsheet.col_values(1)
        named=named_data[1:]
        questions_data = quizsheet.col_values(2)
        questions=questions_data[1:]
        answers_data=quizsheet2.col_values(2)
        return render_template('quiz.html',named=named,questions=questions,name_users=session['name_user']) 
    else:
        return redirect(url_for('login'))

          
@app.route('/ask_question', methods=["GET",'POST'])
def ask_question():
    if session.get('logged_in_user'):
        global name_user
        if request.method == 'POST':
            # Process the submitted question
            question = request.form['question']
            # Write the question to the Google Sheet
            quizsheet.append_row([session['name_user'],question])
            return redirect(url_for('quiz'))  # Redirect to quiz page after submitting question
        return render_template('ask.html')
quizsheet2= client.open("Register Sheet").get_worksheet(2)
@app.route('/submit_answer/<int:question_index>', methods=['POST'])
def submit_answer(question_index):
    global name_user
    if request.method == 'POST':
        answer = request.form['answer']
        question = request.form['question']
        # Write the answer to the Google Sheet
        quizsheet2.append_row([session['name_user'],question, answer])
        return redirect(url_for('quiz'))
    
@app.route("/answers")
def answers():
    global logged_in_user
    if session.get('logged_in_user'):
        named_data=quizsheet2.col_values(1)
        question_data=quizsheet2.col_values(2)
        answers_data=quizsheet2.col_values(3)
        named=named_data[1:]
        questions=question_data[1:]
        answers=answers_data[1:]
        return render_template('answers.html',named=named,questions=questions,answers=answers)
    else:
        return redirect(url_for('login'))
    
quizsheet4= client.open("Register Sheet").get_worksheet(3)
@app.route("/blog")
def blog():
    global name_user
    global logged_in_user
    if session.get('logged_in_user'):   
        blog_data = quizsheet4.get_all_records()
        blog_data.reverse()
        return render_template("blog.html",blog_data=blog_data)
    else:
        return redirect(url_for('login'))
    
@app.route("/createblog")
def createblog():
    global name_user
    global logged_in_user
    if session.get('logged_in_user'):   
        return render_template("createblog.html")
    else:
        return redirect(url_for('login'))
    

@app.route("/submit_blog", methods=['POST'])
def submit_blog():
    global logged_in_user
    global name_user
    if request.method == 'POST':
        if session.get('logged_in_user'):   
            titles = request.form['title']
            contents = request.form['content']
            images = request.files['image']
            image_filename = secure_filename(images.filename)  # Secure filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)  # Save image to the UPLOAD_FOLDER
            images.save(image_path)
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
            quizsheet4.append_row([session['name_user'], titles, contents,current_date,image_filename])
            return redirect(url_for('blog'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
if __name__=="__main__":
    app.run(debug=False)
