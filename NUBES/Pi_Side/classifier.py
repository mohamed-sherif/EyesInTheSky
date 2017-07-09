import argparse
import cv2
import os
import pickle
import sys
import numpy as np

from EITS import specs
from EITS.dbHandler import dbHandler
from NUBES.util.align_dlib import AlignDlib
from NUBES.openface.torch_neural_net import TorchNeuralNet



def load_classifier(ClassiferPath):
    """
    Load the SVM classifier model.

    :param ClassifierPath: Path tp SVM classifier
    return: SVM model(clf) and LabelEncoder(le).
    """    
    with open(ClassiferPath, 'r') as f:
         # le - label and clf - c 
        (le, clf) = pickle.load(f)  

    return(le, clf)



def getRep(bgrImg):
    """
    Prepare the captured frame and feed it 
    To the neural network.

    :param bgrImg: The captured frame
    return: 128-representations of the face.
    """       
    alignedFaces = []
    reps = []

    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    # Get all bounding boxes
    bb = align.OPENCV_getAllFaceBoundingBoxes(rgbImg)
    if bb is None:
        # raise Exception("Unable to find a face: {}".format(imgPath))
        return []

    #align each face
    for box in bb:
        alignedFaces.append(align.align(FLAGS.size,rgbImg,box))

    #feed the each aligned face to the neural network
    #to caluclate the face representations
    for alignedFace in alignedFaces:
        reps.append(net.forward(alignedFace))


    return reps


def infer(img,le,clf):
    """
    Calls getREP() function and predict the returned
    128-reprsentations using the generated SVM model
    from Training.

    :param bgrImg: The captured frame
    return: 128-representations of the face.
    """     
    persons = []
    confidences = []

    reps = getRep(img)
    #if reps is empty it wont enter the loop
    for rep in reps:
        #change shape of (128,) to (1,128) 'as tarined'
        rep = rep.reshape(1, -1)
        #get propapility of predictions
        # 0     1
        #[0.2,0.99]
        predictions = clf.predict_proba(rep).ravel()
        #Take the [i] heighst prediction
        #[0.2,0.99]-->maxI= '1'
        maxI = np.argmax(predictions)
        #get the inverse of the LabelEncoder to get the crossponding label name
        persons.append(le.inverse_transform(maxI))
        #get the propapility of heighst prediction
        #[0.2,o.99]-->prediction[1]=0.99
        confidences.append(predictions[maxI])
        
    return (persons, confidences) 


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
      '--classifier_model',
      type=str,
      default='/home/sherif/Desktop/packagetest/generated-embeddings/classifier.pkl',
      help='Path to classifier folder.'
    )

    parser.add_argument(
      '--network_model',
      type=str,
      default='/home/sherif/Desktop/packagetest/models/openface/nn4.small2.v1.t7',#nn4.v1.ascii
      help='Path to neural_network model folder.'
    ) 

    parser.add_argument(
      '--dlibFacePredictor',
      type=str,
      default='/home/sherif/Desktop/packagetest/models/dlib/shape_predictor_68_face_landmarks.dat',
      help='path to dlib facemark detector classifier.'
    )

    parser.add_argument(
      '--threshold',
      type=float,
      default=0.96,
      help='The threshold for unkown person.'
    )  

    parser.add_argument(
      '--size',
      type=int,
      default=96,
      help='Default image size.'
    )  


    FLAGS, unparsed = parser.parse_known_args()
    
    
    #set the precision of the output
    #0.23445-->0.23
    np.set_printoptions(precision=2)

    pi_mac = specs.getMac() 
    pi_location = notifyLocation(pi_mac)
    #create instance of aligment and neural network classes
    align = AlignDlib(FLAGS.dlibFacePredictor)
    net = TorchNeuralNet(FLAGS.network_model,imgDim=FLAGS.size)
    
    #load the classifier
    le,clf = load_classifier(FLAGS.classifier_model)
    # Capture device. Usually 0 will be webcam and 1 will be usb cam.
    video_capture = cv2.VideoCapture(0)
    #set the width and height == resolution
    video_capture.set(3, 320)
    video_capture.set(4, 240)

    while True:
        ret, frame = video_capture.read()

        persons, confidences = infer(frame,le,clf)
        print ("P: " + str(persons) + " C: " + str(confidences))
#==================================================================================
#update the status of the detected criminal in database
#================================================================================== 

        for i, c in enumerate(confidences):
            if c >= FLAGS.threshold:  # 0.5 is kept as threshold for known face.
                #persons[i] = "_unknown"
                dbHandler.updateCriminalStatus(persons[i],pi_location)
                
#==================================================================================

