import time
import os
import pickle
import cv2
import imutils
from imutils import paths
from imutils.video import VideoStream
import face_recognition
  
"""
facialRecog.py
===============
Acknowledgement
    Code was adapted from TutLab 9 01_capture.py, 02_encode.py, and 03_recognise.py
    which in turn was adapted from
    https://www.hackster.io/mjrobot/real-time-face-recognition-an-end-to-end-project-a10826
    and
    https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/
"""

class FacialRecog():
    """
        This program implements the 3 stages of facial recognition
        1. Capturing the images 
        2. Encoding the images
        3. Recognises the images stored in the dataset and identifies the person
    """
    def __init__(self):
        #get the pre-built classifier that had been trained on 3 million faces
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.cam = cv2.VideoCapture(0)

        #initializes the list of known encodings and known names
        self.knownEncodings = []
        self.knownNames = []

        #this is the image path to the dataset
        self.image_paths = list(paths.list_images('dataset'))

    def CreateFace(self):
        """
        this is where the images will be first captured.
        
        """

        #sets the height and the width of the camera 
        self.cam.set(3,640)
        self.cam.set(4,480)
        
        #takes in the name of the user
        self.face_user = input('\n Enter Username and press Return ')

        #looks for the folder that is being used, in this case it's a folder called dataset
        folder = "./dataset/{}".format(self.face_user)

        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0

        #The ideal amount of photos generated is 10
        #this loop will keep going until 10 is reached or the user quits the program
        while count <= 10:
            key = input("Press q to quit or Enter to continue: ")
            if key == "q":
                break
            
            ret, frame = self.cam.read()
            if not ret:
                break
            
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            
            if(len(faces) == 0):
                print("No face detected, Try again")
                continue
            
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                img_name = "{}/{:04}.jpg".format(folder, count)
                cv2.imwrite(img_name, frame[y : y + h, x : x + w])
                print("{}".format(img_name))

                
                count += 1
                
        self.cam.release()

    

    def encodeFace(self):
        """
        this is where the images taken are encoded into a pickle file
        """

        #Loops through all the images that is stored in the dataset according to the image path

        for (i, image_path) in enumerate(self.image_paths):

            print("Encoding images {}/{} ".format(i + 1, len(self.image_paths)))
            #gets the name from the image path
            name = image_path.split(os.path.sep)[-2]

            #load the input image and converts it from RGB to dlib ordering
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x,y)-coordinates of the bounding boxes
            boxes = face_recognition.face_locations(rgb, model="hog")
            #compute the facial embeddings for the face
            encodings = face_recognition.face_encodings(rgb,boxes)
            #loop over the encodings
            for encoding in encodings:
                self.knownEncodings.append(encoding)
                self.knownNames.append(name)

        print("Serializing Encodings...")
        data ={"encodings": self.knownEncodings, "names": self.knownNames}

        with open('encodings.pickle', "wb") as file:
            file.write(pickle.dumps(data))


    def facial_login(self):
        """
        This is where the program tries to identifiy a face 
        """

        while not os.path.isfile('encodings.pickle'):
            time.sleep(3.0)
        #loading the pickle encodings to allow for facial recognition
        data = pickle.loads(open('encodings.pickle', 'rb').read())

        print('Starting facial Recognition')
        #starts up the videostream
        video_stream = VideoStream(src=0).start()
        time.sleep(2.0)

        while True:
            
            frame = video_stream.read()
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width = 240)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            names = []

            #loops through the facial embeddings
            for encoding in encodings:

                faceMatch = face_recognition.compare_faces(data['encodings'], encoding)
                name = 'Unknown'

                if True in faceMatch:
                    matched_id = [i for (i, b) in enumerate(faceMatch) if b]
                    counts = {}
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched

                    for i in matched_id:
                        name = data['names'][i]
                        counts[name] = counts.get(name,0) + 1

                    name = max(counts, key=counts.get)
                names.append(name)

            for name in names:
                print("Person Found: {}".format(name))
                time.sleep(3.0)
        video_stream.stop()
