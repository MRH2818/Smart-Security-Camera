# Importing modules

# Manages camera
import video_camera as vc

# Sends email notifications
from email_sender import send_email_message, send_url_message

# For file reading
import os

# For mulithreading
import threading

# For the Flask webserver
from flask import Flask, render_template, Response, jsonify, send_from_directory, request, redirect, make_response

# For CSV file manipulation
import pandas as pd

# Initalize Flask app
app = Flask(__name__)

# Initialize settings variable
settings = {}

# Load settings from CSV file
if (os.path.exists(os.path.join(app.root_path, "Data", "settings.csv"))) :
    settings_data_frame = pd.read_csv(os.path.join(app.root_path, "Data", "settings.csv"))
    
    # Setting dict format as "records" organizes dict as [ {"columnName" : value1}, {"columnName" : value2} ]
    settings = settings_data_frame.to_dict('records')[0]

else :
    # If there isn't a settings CSV file, load settings
    defaultSettings = { "recTolerance" : [0.55],
        "certifyTolerance" : [0.4],
        "imageDifferenceTol" : [0.1],
        "minPercOfPosImgs" : [0.2],
        "confirmationTime" : [5] }

    settings_data_frame = pd.DataFrame(defaultSettings);
    settings_data_frame.to_csv(os.path.join(app.root_path, "Data", "settings.csv"))

# Initialize global variables. The constructor for the Video_Camera class will familiarize faces, which can take a while
sec_camera = vc.Video_Camera(0, settings=settings)
status = dict()

# This loop variable basically decides whether or not to continue the continuous thread
loop = True

# Loads the person log files
person_log_file_path = os.path.join("Data", "recentVisitors.csv")
person_html_log_file_path = os.path.join("templates", "personLog.html")

# Continuous funtion checks camera and analyzes data
def manage_guards() :
    # These variables are used to determine the last time a person was logged. 
    last_log = vc.time.time()
    last_email = vc.time.time() - 1200
    last_person = ""

    while loop :
        global status
        status = sec_camera.patrol()
        
        # print (status, start)

        # Checks if the status is empty. If it is, then there must have been some kind of problem with the camera
        if (status["Person"] != None) :
            # Log person event into data. I created this parameter boolean to make my code more readable.
            parameter2 = (status["Person"] != last_person and vc.time.time() - last_log >= 60)
            
            # Checks if the last time a person was logged was over 3 minutes ago or a new person has been discovered in the past 60 seconds
            if ((vc.time.time() - last_log >= 180) or parameter2) :
                log_data_frame = None

                # Reset log timer
                last_log = vc.time.time()

                # Logs person
                if (os.path.exists(person_log_file_path) == False) :
                    log_data_frame = pd.DataFrame({"Timestamp" : [vc.time.asctime()], "Person" : [ status["Person"] ]})
                else :
                    log_data_frame = pd.read_csv(person_log_file_path, index_col=0)
                    log_data_frame = log_data_frame.append(pd.DataFrame({"Timestamp" : [vc.time.asctime()], "Person" : [ status["Person"] ]}), ignore_index=True)
                
                # Saves log to csv file and html file for website
                log_data_frame.to_csv(person_log_file_path)
                log_data_frame.to_html(person_html_log_file_path)

                #print("Logged Guy")
                #print(logDataFrame)
                last_person = status["Person"]

                # Send email if environment is not safe
                if (status["Status"] != "Safe" and vc.time.time() - last_email >= 1200) :

                    # Save image frame as local file
                    image_destination = os.path.join("Data", "surveilancePhoto.jpeg")
                    vc.cv2.imwrite(image_destination, sec_camera.current_image)

                    print("Sending Email")

                    # For some reason, emails can't be sent from my Windows computer, but they work fine on my Raspberry Pi

                    try :
                        send_email_message(image_destination, person_name=status["Person"], image_type="jpeg", image_file_name="Surveilance Photo.jpeg")
                    except :
                        print("Error sending email message")
                    
                    # Reset email timer
                    last_email = vc.time.time()


# Initiate continous thread function. Points to manageGuards function
thread = threading.Thread(target = manage_guards)

thread.setDaemon(True)
thread.start()
thread.setName("The_Manager")
print("Thread initiated")


# My absolutely terrible encryption thing. It basically just combines all of the string's characters into one. I thought it would be fun to make my own instead of using a SHA algorithm
def quick_encrypt (string_to_encrypt) :
    ch = 0
    for character in string_to_encrypt :
        ch += ord(character)
    return chr(ch)


# Events for Flask app
@app.route("/", methods=["GET"])
def getWebPage () :
    # Checks a cookie. If cookie is bad, redirect the webpage to the login form
    if (request.cookies.get("userId") != quick_encrypt(username)) :
        return redirect("/appLogin")
    return render_template("template.html")


# Login form details. If I were to further develop this, I would use environment variables instead,
# but I hacked toghether this system in less than a day. Please excuse this, I had a lot of schoolwork.

username = "TerribleUsername"
password = "AtrociousPassword"

# App login
@app.route("/appLogin", methods=["GET"])
def get_login_form () :
    return render_template("loginTemplate.html")

# Login form
@app.route("/requests/login", methods=["POST"])
def handle_login_information() :
    # Delay to discourage brute-forcing attacks. I figured that when random people on the internet decide to
    # hack a 13-year-old's personal project, they will get bored when they have to wait for longer.
    vc.time.sleep(5)

    # Checks form data recieved.
    if (request.form["password"] == password and request.form["user"] == username) :
        resp = make_response(redirect("/"))

        # Sets a familiar cookie on the user's web browser so I don't have to login every single time I want to access the webpage.
        resp.set_cookie("userId", quick_encrypt(username))
        return resp
    else :
        return redirect("/appLogin")

# Shutdown camera post request handler
@app.route("/information/shutdown", methods=["POST"])
def handle_shutdown_request() :
    # Checks username and password
    if (request.form["password"] == password and request.form["user"] == username) :
        # Stops managingGuards function
        global loop
        loop = False
        os.system("sudo shutdown 1")
        return redirect("/")

    else :
        return redirect("/")


# Person log
@app.route("/information/personLog")
def view_person_log() :
    # Checks page cookies
    if (request.cookies.get("userId") != quick_encrypt(username)) :
        return redirect("/appLogin")
    resp = None
    try :
        # render_template function doesn't always update when the file is cleared, so this is my alternative
        html_log = open(person_html_log_file_path, "r")
        text = html_log.read()
        resp = text
    except :
        resp = "<h1>Error 500</h1><h2>Can't Retrieve Person Log</h2>"
    return resp

@app.route("/information/personLog/clear", methods=["POST"])
def clear_person_log() :
    print ("Cleared log")


    fileData = open(person_html_log_file_path, "w")
    fileData.write("<h1>This is empty.</h1>")
    fileData.close()

    # Deletes person log file
    os.remove(person_log_file_path)

    return redirect("/")


# Generator to get camera data
def frame_gen(camera) :
    while True :
        # We need to format the camera frame this special way before we compile them into multi-image media format for the room's livestream
        jpg_frame_format = camera.getFrame()
        yield (b'--frame\r\n' + b'Content-Type: image/jpg\r\n\r\n' + jpg_frame_format + b'\r\n\r\n')


"""while True :
    print(next(frameGen(Video_Camera(0)))[1])"""

# Livestream for room
@app.route("/information/raw_video_feed", methods=["GET"])
def get_video_frame() :
    # Response function calls generator automatically and creates a mixed-image file that the client will look for.
    return Response(frame_gen(sec_camera), mimetype='multipart/x-mixed-replace; boundary=frame;')

# Get room status. This is meant to be polled on the client side
@app.route("/information/status", methods=["GET"])
def get_status() :
    return jsonify(status)

# This returns the script for the long poller
@app.route("/information/JSCode/poller.js", methods=["GET"])
def working_poller() :
    return send_from_directory(os.path.join(app.root_path, "JavaScript"), 'poller.js', mimetype="text/javascript")

# This is a script that calls for the camera's settings so that it can change them
@app.route("/information/JSCode/retrieveSettings.js", methods=["GET"])
def get_settings_script() :
    return send_from_directory(os.path.join(app.root_path, "JavaScript"), 'retrieveSettings.js', mimetype="text/javascript")

# Returns an icon for the website
@app.route("/information/favicon.ico", methods=["GET"])
def get_favicon() :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon.ico', mimetype="image/x-icon")


# These icons must be in the root folder for Apple's Safari add-to-homescreen feature
@app.route("/apple-touch-icon.png", methods=["GET"])
def get_apple_home_screen_icon_for_iphone_x () :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon_iPhoneX.png', mimetype="image/png")

@app.route("/apple-touch-icon-120x120.png")
def get_apple_home_screen_icon_for_120_120px () :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon_120x120.png', mimetype="image/png")

# Update facial recognition settings from client
@app.route("/information/settings/update", methods=["POST"])
def update_settings () :
    print(request.form.to_dict())
    global sec_camera

    sec_camera.rec_tolerance = float(request.form["recTol"]);
    sec_camera.certify_tolerance = float(request.form["certTol"]);
    sec_camera.image_difference_tolerance = float(request.form["imgDiffTol"]);
    sec_camera.min_perc_of_pos_images = float(request.form["minPerc"]);
    sec_camera.confirmation_time = float(request.form["confirmTime"]);

    settings = { "recTolerance" : [sec_camera.rec_tolerance],
        "certifyTolerance" : [sec_camera.certify_tolerance],
        "imageDifferenceTol" : [sec_camera.image_difference_tolerance],
        "minPercOfPosImgs" : [sec_camera.min_perc_of_pos_images],
        "confirmationTime" : [sec_camera.confirmation_time] }

    settings_data_frame = pd.DataFrame(settings);
    settings_data_frame.to_csv(os.path.join(app.root_path, "Data", "settings.csv"))
    
    return redirect("/")

# Hand facial recognition settings to client. The retrieve settings JavaScript code file sends a request to this
@app.route("/information/settings/retrieve", methods=["GET"])
def get_settings () :
    settings = { "recTolerance" : sec_camera.rec_tolerance,
        "certifyTolerance" : sec_camera.certify_tolerance,
        "imageDifferenceTol" : sec_camera.image_difference_tolerance,
        "minPercOfPosImgs" : sec_camera.min_perc_of_pos_images,
        "confirmationTime" : sec_camera.confirmation_time }

    return jsonify(settings)


# On my Raspberry Pi, I have extra code here that establishes an ngrok connection for
# port 5000, and sends me an email containing its tunnel URL. I used this so I can
# access my camera from anywhere on the internet.

# from pyngrok import ngrok

# try :
#   url = ngrok.connect(5000).public_url
#   send_url_message(url)
# except :
#   print ("Error establishing ngrok")

if (__name__ == "__main__") :
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader = False)

