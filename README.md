# Smart Security Camera

These are the project files for a program I made that uses facial recognition, with the face_recognition Python library, to detect "unauthorized" people (parents) in my room. If there is a parent or someone the camera doesn't recognize in my room, it will send me an email.

The security camera also runs a web server I coded using the Flask framework, which mostly runs a single page. The main page consists of a live stream of my room, a pop-up that allows you to change the way that the program handles results from the facial recognition library, a link to a table where you can see a log of everyone who entered my room, and a few more features that I encourage you to check out.

There is also a login page I quickly scrapped toghether. I wasn't quite sure how to make this properly, so I am especially open to any advice you may have on this feature.

The program is meant to run from my Raspberry Pi Model 4 B, which is equiped with 8GB of RAM and runs the Raspbian operating system.

I am more than open to any suggestions you may have about my approach to this project and my code.

Facial Recognition Library:
https://pypi.org/project/face-recognition/

Flask Framework:
https://pypi.org/project/Flask/

