import smtplib
import json
import os
from email.message import EmailMessage

def load_config_file () :
    file_text = ""
    with open(os.path.join("Data", "config.json"), "r") as file_data :    
        file_text = "".join(file_data.readlines())
    
    return json.loads(file_text)

def send_email_message (file_path, person_name, image_type="jpeg", image_file_name="Surveilance Photo.jpeg") :
    # Load data from config file
    config = load_config_file()
    
    # Format message
    message = EmailMessage()

    message["Subject"] = "Alert From Your Security Camera"
    message["From"] = config["email_sender"]
    message["To"] = config["email_recipient"]

    message.set_content(f'Dear Max,\n\n{person_name} has entered your room. Please do not worry, this incident has been logged.\n\nUntil next time,\nMax\'s Security Camera')

    file_data = None
    with open(file_path, 'rb') as file :
        file_data = file.read()
    
    message.add_attachment(file_data, maintype="image", subtype=image_type, filename=image_file_name)

    # Establish connection and send message
    with smtplib.SMTP_SSL(config["email_network_smtp_address"], config["email_network_port"]) as smtpConn :
        smtpConn.login(config["email_sender"], config["email_sender_pass"])
        smtpConn.send_message(message)

def send_url_message (url) :
    # Load data from config file
    config = load_config_file()

    message = EmailMessage()
    message["Subject"] = "Your Ngrok Tunnel URL"
    message["From"] = config["email_sender"]
    message["To"] = config["email_recipient"]

    message.set_content(f'Dear Max,\n\nThe Ngrok tunnel URL for your security camera is {url}\n\n'
        + "Until next time,\nMax's Security Camera")

    with smtplib.SMTP_SSL(config["email_network_smtp_address"], config["email_network_port"]) as smtpConn :
        smtpConn.login(config["email_sender"], config["email_sender_pass"])
        smtpConn.send_message(message)
