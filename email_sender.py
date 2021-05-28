import smtplib
from email.message import EmailMessage

def send_email_message (file_path, person_name, image_type="jpeg", image_file_name="Surveilance Photo.jpeg") :
    # Format message
    message = EmailMessage()

    message["Subject"] = "Alert From Your Security Camera"
    message["From"] = "TerribleUsername01@gmail.com"
    message["To"] = "TerribleUsername00@ucc.on.ca"

    message.set_content(f'Dear Max,\n\n{person_name} has entered your room. Please do not worry, this incident has been logged.\n\nUntil next time,\nMax\'s Security Camera')

    file_data = None
    with open(file_path, 'rb') as file :
        file_data = file.read()
    
    message.add_attachment(file_data, maintype="image", subtype=image_type, filename=image_file_name)

    # Establish connection and send message
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtpConn :
        smtpConn.login("TerribleUsername01@gmail.com", "AtrociousPassword")

        # Send message
        smtpConn.send_message(message)

# For the Specifically for Ngrok Tunnel URL
def send_url_message (url) :
    message = EmailMessage()
    message["Subject"] = "Your Ngrok Tunnel URL"
    message["From"] = "TerribleUsername01@gmail.com"
    message["To"] = "TerribleUsername00@gmail.com"

    message.set_content(f'Dear Max,\n\nThe Ngrok tunnel URL for your security camera is {url}\n\n'
        + "Until next time,\nMax's Security Camera")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_conn :
        smtp_conn.login("TerribleUsername01@gmail.com", "AtrociousPassword")
        smtp_conn.send_message(message)
