import smtplib
from email.message import EmailMessage

def sendEmailMessage (filePath, personName, imageType="jpeg", imageFileName="Surveilance Photo.jpeg") :
    # Format message
    message = EmailMessage()

    message["Subject"] = "Alert From Your Security Camera"
    message["From"] = "TerribleUsername01@gmail.com"
    message["To"] = "TerribleUsername00@ucc.on.ca"

    message.set_content(f'Dear Max,\n\n{personName} has entered your room. Please do not worry, this incident has been logged.\n\nUntil next time,\nMax\'s Security Camera')

    file_data = None
    with open(filePath, 'rb') as file :
        file_data = file.read()
    
    message.add_attachment(file_data, maintype="image", subtype=imageType, filename=imageFileName)

    # Establish connection and send message
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtpConn :
        smtpConn.login("TerribleUsername01@gmail.com", "AtrociousPassword")

        # Send message
        smtpConn.send_message(message)

# For the Specifically for Ngrok Tunnel URL
def sendURLMessage (url) :
    message = EmailMessage()
    message["Subject"] = "Your Ngrok Tunnel URL"
    message["From"] = "TerribleUsername01@gmail.com"
    message["To"] = "TerribleUsername00@gmail.com"

    message.set_content(f'Dear Max,\n\nThe Ngrok tunnel URL for your security camera is {url}\n\n'
        + "Until next time,\nMax's Security Camera")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtpConn :
        smtpConn.login("TerribleUsername01@gmail.com", "AtrociousPassword")
        smtpConn.send_message(message)
