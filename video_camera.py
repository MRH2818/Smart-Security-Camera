# Executes facial recognition
import face_recognition

# Manipulates images
import cv2

# File system manager
import os

# Keeps track of time for timers
import time

# Parses JSON data from files
import json

from numpy.lib.function_base import average

global_known_faces_dir = "C:\\Users\\codr9\\OneDrive\\Desktop\\Coding files\\Python\\Projects\\Security Camera\\known_faces"

class Video_Camera :
    # Class constructor
    def __init__ (self, cameraNum, preKnownFaces = [], preSafeNames = [], settings = { "recTolerance" : 0.55,
        "certifyTolerance" : 0.4,
        "imageDifferenceTol" : 0.1,
        "minPercOfPosImgs" : 0.2,
        "confirmationTime" : 5 }) :

        #Instantiating variables
        self.known_faces_dir = global_known_faces_dir
        
        self.error_message = cv2.imread("C:\\Users\\codr9\\OneDrive\\Desktop\\Coding files\\Python\\Projects\\Security Camera\\ErrorImage.jpeg")

        # List of dictionaries designed like so:
        # [{"PersonName" : [LIST_OF_FACE_ENCODINGS]}]
        self.known_faces = preKnownFaces
        
        # Is a list of people that are considered "safe"
        self.safe_names = preSafeNames

        # Retrieves frames from camera
        self.video = cv2.VideoCapture(cameraNum)

        # Keeps track of current frames
        self.current_image = self.video.read()[1]

        # Lower is stricter        
        # The amount of difference allowed between two faces
        self.rec_tolerance = settings["recTolerance"]
        
        # Amount of difference between two camera frames that the program will accept as a person
        self.image_difference_tolerance = settings["imageDifferenceTol"]

        # Higher is stricter
        # The percentage of how many most repeating matches there must be for the program to finally accept it
        self.min_perc_of_pos_images = settings["minPercOfPosImgs"]
        
        # The program will wait this much time before definitively ruling a match
        self.confirmation_time = settings["confirmationTime"]

        # The percentage of how many most repeating matches there must be for the program to consider it
        self.certify_tolerance = settings["certifyTolerance"]

        if (self.known_faces == []) :
            self.load_faces()
        if (self.safe_names == []) :
            self.load_names()

    def __del__ (self) :
        self.video.release()
        print("Video Released")

    # Load faces
    def load_faces (self) :
        counter = 0
        for name in os.listdir(self.known_faces_dir) :
        
            if (name.endswith(".json")) :
                continue
            
            print ("\n" + f"Learning {name}'s face")

            #To see if the face is invalid. We don't want to add a known face,
            #if all of the sample images are invalid
            invalidface = True

            self.known_faces.append({name : []})

            # Loops through known faces folder
            for profile in os.listdir(os.path.join(self.known_faces_dir, name)) :
                print(profile)

                image = face_recognition.load_image_file(os.path.join(self.known_faces_dir, name, profile))
                prof_encodings = face_recognition.face_encodings(image)

                if (prof_encodings == []) :
                    # Throw an error or something, as the list of encodings is empty,
                    # and the program failed to find a face
                    return "Error: image has multiple faces"
            
                # Adding the face encodings to the list
                self.known_faces[counter][name].append(prof_encodings[0])

                # Confirming whether or not the face is illegible
                invalidFace = False

            if (invalidFace == True) :
                self.known_faces.remove({name : []})
                continue

            counter += 1

    # Load authorized names
    def load_names (self) :
        #try :
        # Loops through known faces folder
        for file in os.listdir(self.known_faces_dir) :
            if (file.endswith(".json") == True) :
                file_data = open(os.path.join(self.known_faces_dir, file), "r")
                file_text = "".join(file_data.readlines())

                file_data.close()

                person_data = json.loads(file_text)

                if (person_data["auth"] == "safe") :
                    self.safe_names.append(person_data["name"])

        #except :
            #print("Error loading names")


    # This function does not have a continuous loop, niether is it recursive, so it
    # must be called with an exterior loop
    def patrol (self) :
        new_frame = None

        try :
            new_frame = self.video.read()[1]
            testPants = new_frame[1]

        except :
            print("Can't get frame")
            self.current_image = self.error_message
            # cv2.imshow("Hello!", self.current_image)

            # cv2.waitKey(0)
            return {"Status" : "Unknown", "Person" : False, "Positivity" : 1}


        blue, green, red = cv2.split(self.current_image)
        bdif, gdif, rdif = cv2.split(cv2.subtract(new_frame, self.current_image))

        frame_full_pix_average = (cv2.countNonZero(blue) + cv2.countNonZero(green) + cv2.countNonZero(red)) / 3
        difference_full_pix_avg = (cv2.countNonZero(bdif) + cv2.countNonZero(gdif) + cv2.countNonZero(rdif)) / 3

        self.current_image = new_frame

        diff_ration = (difference_full_pix_avg / frame_full_pix_average)
        diff_ratio_sum = diff_ration

        # Will be calculated at the end of this loop
        avg_diff_ratio = 0

        #Starting the timer
        start = time.time()
        match_histogram = {}

        while time.time() - start < self.confirmation_time :
            new_frame = self.video.read()[1]

            bdif, gdif, rdif = cv2.split(cv2.subtract(new_frame, self.current_image))
            difference_full_pix_avg = (cv2.countNonZero(bdif) + cv2.countNonZero(gdif) + cv2.countNonZero(rdif)) / 3
            diff_ration = (difference_full_pix_avg / frame_full_pix_average)

            self.current_image = new_frame
            encodings = face_recognition.face_encodings(self.current_image)

            #If there is no face detected in this video frame
            if (encodings == []) :
                continue
            
            # Shortens list down to one face. This makes it so that the camera detects the first face it sees
            encodings = [ encodings[0] ]

            for face_encoding in encodings :
                #counter = 0

                #print (self.knownFaces[counter])
                for face_pair in self.known_faces :
                    #print(facePair)
                    name = list(face_pair.keys())[0]
                    person_encodings = list(face_pair.values())[0]
                    
                    results = face_recognition.compare_faces(person_encodings, face_encoding, tolerance=self.rec_tolerance)
                    
                    if (self.certify_result(results)) :
                        #Log the match into the histogram
                        match_histogram[name] = match_histogram.get(name, 0) + 1

                    else :
                        match_histogram[name + "_false"] = match_histogram.get(name + "_false", 0) + 1
                        
                        # I AM VERY AWARE THAT HAVING MORE THAN ONE VALUE IN A DICTIONARY LIKE THIS MAKES ME A PYTHON OUTLAW.
                        # I did this because I wasn't sure what I wanted to call people the camera couldn't recognize. I still
                        # am somewhat indecisive about this, but I settled on "Unknown"
                        match_histogram[False] = match_histogram.get(False, 0) + 1
                    #counter += 1
        
        potential_person = self.get_common_guy(match_histogram)

        if (potential_person["name"] == True) :
            # print("No matches!!")
            # Check if frame is drastically different, because there may be a person moving
            # print(tempratio)
            if (diff_ration > self.image_difference_tolerance) :
                return {"Status" : "Breached", "Person" : "Unknown", "Positivity" : (1 - diff_ration)}
            return {"Status" : "Safe", "Person" : None, "Positivity" : potential_person["positivity"]}

        if (potential_person["name"] == False) :
            #print("UNKNOWN")
            return {"Status" : "Breached", "Person" : "Unknown", "Positivity" : potential_person["positivity"]}

        # Person is detected
        # Check if person is authorized
        status = "Breached"

        if (potential_person["name"] in self.safe_names) :
            status = "Safe"

        return {"Status" : status, "Person" : potential_person["name"], "Positivity" : potential_person["positivity"]}
    

    # Results is a list of booleans
    # This function decides whether there are enough True values in the results list to rule the face
    # as a match before it moves onto other security features.
    def certify_result(self, results) :
        length = len(results)
        good_results = 0

        for result in results :
            if (result == True) :
                good_results += 1
                if (good_results / length >= self.certify_tolerance) :
                    return True

        return False

    # Looks at the results from the histogram dictionary and chooses the highest value
    def get_common_guy(self, result_histogram) :
        if (result_histogram == {}) :
            # Name is equal to true if there are no results
            return {"positivity" : 1, "name" : True}

        # print(resultHistogram)

        largest_recurence = 0
        positive_person_name = 0
        total_recurences = 0

        for name, recurences in result_histogram.items() :
            if (type(name) != type(bool(True))) :
                if (name.endswith("_false")) :
                    continue

            total_recurences += recurences

            if (recurences > largest_recurence) :
                positive_person_name = name
                largest_recurence = recurences
            
        
        if (positive_person_name != False) :
            positivity_ratio = 1 - (result_histogram.get(positive_person_name + "_false", 0) / largest_recurence)
            if (positivity_ratio > self.min_perc_of_pos_images) :
                return {"positivity" : positivity_ratio, "name" : positive_person_name}
        
        return { "positivity" : (largest_recurence / total_recurences), "name" : False }
    
    
    def get_frame(self) :
        frame = self.video.read()[1]
        
        # Checks if frame is empty, meaning that there was some sort of error retrieving the camera frame
        try :
            pants = frame[0]
        except :
            frame = self.error_message
        
        return cv2.imencode(".jpg", frame)[1].tobytes()

