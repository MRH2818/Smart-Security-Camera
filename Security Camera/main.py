# Importing modules

# Manages camera
import video_camera as vc

# Sends email notifications
from emailSender import sendEmailMessage, sendURLMessage

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
    settingsDataFrame = pd.read_csv(os.path.join(app.root_path, "Data", "settings.csv"))
    
    # Setting dict format as "records" organizes dict as [ {"columnName" : value1}, {"columnName" : value2} ]
    settings = settingsDataFrame.to_dict('records')[0]

else :
    # If there isn't a settings CSV file, load settings
    defaultSettings = { "recTolerance" : [0.55],
        "certifyTolerance" : [0.4],
        "imageDifferenceTol" : [0.1],
        "minPercOfPosImgs" : [0.2],
        "confirmationTime" : [5] }

    settingsDataFrame = pd.DataFrame(defaultSettings);
    settingsDataFrame.to_csv(os.path.join(app.root_path, "Data", "settings.csv"))

# Initialize global variables. The constructor for the Video_Camera class will familiarize faces, which can take a while
secCamera = vc.Video_Camera(0, settings=settings)
status = dict()

# This loop variable basically decides whether or not to continue the continuous thread
loop = True

# Loads the person log files
personLogFilePath = os.path.join("Data", "recentVisitors.csv")
personHtmlLogFilePath = os.path.join("templates", "personLog.html")

# Continuous funtion checks camera and analyzes data
def manageGuards() :
    # These variables are used to determine the last time a person was logged. 
    lastLog = vc.time.time()
    lastEmail = vc.time.time() - 1200
    lastPerson = ""

    while loop :
        global status
        status = secCamera.patrol()
        
        # print (status, start)

        # Checks if the status is empty. If it is, then there must have been some kind of problem with the camera
        if (status["Person"] != None) :
            # Log person event into data. I created this parameter boolean to make my code more readable.
            parameter2 = (status["Person"] != lastPerson and vc.time.time() - lastLog >= 60)
            
            # Checks if the last time a person was logged was over 3 minutes ago or a new person has been discovered in the past 60 seconds
            if ((vc.time.time() - lastLog >= 180) or parameter2) :
                logDataFrame = None

                # Reset log timer
                lastLog = vc.time.time()

                # Logs person
                if (os.path.exists(personLogFilePath) == False) :
                    logDataFrame = pd.DataFrame({"Timestamp" : [vc.time.asctime()], "Person" : [ status["Person"] ]})
                else :
                    logDataFrame = pd.read_csv(personLogFilePath, index_col=0)
                    logDataFrame = logDataFrame.append(pd.DataFrame({"Timestamp" : [vc.time.asctime()], "Person" : [ status["Person"] ]}), ignore_index=True)
                
                # Saves log to csv file and html file for website
                logDataFrame.to_csv(personLogFilePath)
                logDataFrame.to_html(personHtmlLogFilePath)

                #print("Logged Guy")
                #print(logDataFrame)
                lastPerson = status["Person"]

                # Send email if environment is not safe
                if (status["Status"] != "Safe" and vc.time.time() - lastEmail >= 1200) :

                    # Save image frame as local file
                    imageDestination = os.path.join("Data", "surveilancePhoto.jpeg")
                    vc.cv2.imwrite(imageDestination, secCamera.current_image)

                    print("Sending Email")

                    # For some reason, emails can't be sent from my Windows computer, but they work fine on my Raspberry Pi

                    try :
                        sendEmailMessage(imageDestination, personName=status["Person"], imageType="jpeg", imageFileName="Surveilance Photo.jpeg")
                    except :
                        print("Error sending email message")
                    
                    # Reset email timer
                    lastEmail = vc.time.time()


# Initiate continous thread function. Points to manageGuards function
thread = threading.Thread(target = manageGuards)

thread.setDaemon(True)
thread.start()
thread.setName("The_Manager")
print("Thread initiated")


# My absolutely terrible encryption thing. It basically just combines all of the string's characters into one. I thought it would be fun to make my own instead of using a SHA algorithm
def quickEncrypt (stringToEncrypt) :
    ch = 0
    for character in stringToEncrypt :
        ch += ord(character)
    return chr(ch)


# Events for Flask app
@app.route("/", methods=["GET"])
def getWebPage () :
    # Checks a cookie. If cookie is bad, redirect the webpage to the login form
    if (request.cookies.get("userId") != quickEncrypt(username)) :
        return redirect("/appLogin")
    return render_template("template.html")


# Login form details. If I were to further develop this, I would use environment variables instead,
# but I hacked toghether this system in less than a day. Please excuse this, I had a lot of schoolwork.

username = "TerribleUsername"
password = "AtrociousPassword"

# App login
@app.route("/appLogin", methods=["GET"])
def getLoginForm () :
    return render_template("loginTemplate.html")

# Login form
@app.route("/requests/login", methods=["POST"])
def handleLoginInformation() :
    # Delay to discourage brute-forcing attacks. I figured that when random people on the internet decide to
    # hack a 13-year-old's personal project, they will get bored when they have to wait for longer.
    vc.time.sleep(5)

    # Checks form data recieved.
    if (request.form["password"] == password and request.form["user"] == username) :
        resp = make_response(redirect("/"))

        # Sets a familiar cookie on the user's web browser so I don't have to login every single time I want to access the webpage.
        resp.set_cookie("userId", quickEncrypt(username))
        return resp
    
    else :
        return redirect("/appLogin")

# Shutdown camera post request handler
@app.route("/information/shutdown", methods=["POST"])
def handleShutdownRequest() :
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
def viewPersonLog() :
    # Checks page cookies
    if (request.cookies.get("userId") != quickEncrypt(username)) :
        return redirect("/appLogin")
    resp = None
    try :
        # render_template function doesn't always update when the file is cleared, so this is my alternative
        htmlLog = open(personHtmlLogFilePath, "r")
        text = htmlLog.read()
        resp = text
    except :
        resp = "<h1>Error 500</h1><h2>Can't Retrieve Person Log</h2>"
    return resp

@app.route("/information/personLog/clear", methods=["POST"])
def clearPersonLog() :
    print ("Cleared log")


    fileData = open(personHtmlLogFilePath, "w")
    fileData.write("<h1>This is empty.</h1>")
    fileData.close()

    # Deletes person log file
    os.remove(personLogFilePath)

    return redirect("/")


# Generator to get camera data
def frameGen(camera) :
    while True :
        # We need to format the camera frame this special way before we compile them into multi-image media format for the room's livestream
        jpgFrameFormat = camera.getFrame()
        yield (b'--frame\r\n' + b'Content-Type: image/jpg\r\n\r\n' + jpgFrameFormat + b'\r\n\r\n')


"""while True :
    print(next(frameGen(Video_Camera(0)))[1])"""

# Livestream for room
@app.route("/information/raw_video_feed", methods=["GET"])
def getVideoFrame() :
    # Response function calls generator automatically and creates a mixed-image file that the client will look for.
    return Response(frameGen(secCamera), mimetype='multipart/x-mixed-replace; boundary=frame;')

# Get room status. This is meant to be polled on the client side
@app.route("/information/status", methods=["GET"])
def getStatus() :
    return jsonify(status)

# This returns the script for the long poller
@app.route("/information/JSCode/poller.js", methods=["GET"])
def workingPoller() :
    return send_from_directory(os.path.join(app.root_path, "JavaScript"), 'poller.js', mimetype="text/javascript")

# This is a script that calls for the camera's settings so that it can change them
@app.route("/information/JSCode/retrieveSettings.js", methods=["GET"])
def getSettingsScript() :
    return send_from_directory(os.path.join(app.root_path, "JavaScript"), 'retrieveSettings.js', mimetype="text/javascript")

# Returns an icon for the website
@app.route("/information/favicon.ico", methods=["GET"])
def getFavicon() :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon.ico', mimetype="image/x-icon")


# These icons must be in the root folder for Apple's Safari add-to-homescreen feature
@app.route("/apple-touch-icon.png", methods=["GET"])
def getAppleHomeScreenIcon_ForiPhoneX () :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon_iPhoneX.png', mimetype="image/png")

@app.route("/apple-touch-icon-120x120.png")
def getAppleHomeScreenIcon_For120x120px () :
    return send_from_directory(os.path.join(app.root_path, "templates"), 'WebsiteIcon_120x120.png', mimetype="image/png")

# Update facial recognition settings from client
@app.route("/information/settings/update", methods=["POST"])
def updateSettings () :
    print(request.form.to_dict())

    global secCamera

    secCamera.recTolerance = float(request.form["recTol"]);
    secCamera.certifyTolerance = float(request.form["certTol"]);
    secCamera.imageDifferenceTolerance = float(request.form["imgDiffTol"]);
    secCamera.minPercOfPosImages = float(request.form["minPerc"]);
    secCamera.confirmationTime = float(request.form["confirmTime"]);

    settings = { "recTolerance" : [secCamera.recTolerance],
        "certifyTolerance" : [secCamera.certifyTolerance],
        "imageDifferenceTol" : [secCamera.imageDifferenceTolerance],
        "minPercOfPosImgs" : [secCamera.minPercOfPosImages],
        "confirmationTime" : [secCamera.confirmationTime] }

    settingsDataFrame = pd.DataFrame(settings);
    settingsDataFrame.to_csv(os.path.join(app.root_path, "Data", "settings.csv"))
    
    return redirect("/")

# Hand facial recognition settings to client. The retrieve settings JavaScript code file sends a request to this
@app.route("/information/settings/retrieve", methods=["GET"])
def getSettings () :
    settings = { "recTolerance" : secCamera.recTolerance,
        "certifyTolerance" : secCamera.certifyTolerance,
        "imageDifferenceTol" : secCamera.imageDifferenceTolerance,
        "minPercOfPosImgs" : secCamera.minPercOfPosImages,
        "confirmationTime" : secCamera.confirmationTime }

    return jsonify(settings)


# On my Raspberry Pi, I have extra code here that establishes an ngrok connection for
# port 5000, and sends me an email containing its tunnel URL. I used this so I can
# access my camera from anywhere on the internet.

# from pyngrok import ngrok

# try :
#   url = ngrok.connect(5000).public_url
#   sendURLMessage(url)
# except :
#   print ("Error establishing ngrok")

if (__name__ == "__main__") :
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader = False)

