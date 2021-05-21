  # Smart-Security-Camera

These are the project files for a program I made that uses a facial recognition, with the face_recognition Python library, to detect "unauthorized" people (parents) in my room. If there is a parent in my room, it will send me an email.

The security camera also runs a website I coded using the Flask framework, which runs from one main page. The main page consists of a live stream of my room, a pop-up that allows you to change the way that the program handles results from the facial recognition library, and a link to a table where you can see a log of everyone who entered my room.

The program is meant to run from my Raspberry Pi Model 4 B, which is equiped with 8GB of RAM.

Facial Recognition Library:
https://pypi.org/project/face-recognition/

Flask Framework:
https://pypi.org/project/Flask/

