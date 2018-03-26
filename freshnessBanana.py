# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import cv2
import time

def get_freshness_model():
    print("Load banana Model")
    model=load_model('banana.h5')
    def freshnessBanana(name):
        # load the image
        start_time=time.time()
        image = cv2.imread(name)
        orig = image.copy()
         
        # pre-process the image for classification
        image = cv2.resize(image, (250, 250))
        image = image.astype("float") / 255.0
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        
        # load the trained convolutional neural network
        print("[INFO] loading network...")
        
        
        # classify the input image
        (post, right, pre)= model.predict(image)[0]
        
        # build the label
        date=None
        if pre>post and pre>right:
            label="can wait"
            date="eat within 10 days"
        elif right>post and right>pre:
            label="eat now"
            date="eat within 3 days"
        elif post>right and post>pre:
            label="gone bad"
            date="do not eat "
            
        if pre>post and pre>right:
            proba=pre
        elif right>post and right>pre:
            proba=right
        elif post>right and post>pre:
            proba=post
        label = "{}: {:.2f}%".format(label, proba * 100)
        label=label+":"+date

        #print (label)
        return label
    return freshnessBanana
    # draw the label on the image
    #output = imutils.resize(orig, width=400)
    #cv2.putText(output, label, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,
    ##	0.7, (0, 255, 0), 2)
    #elapsed_time = time.time() - start_time
    #print("Test data takes ",elapsed_time," seconds")
    # show the output image
    #cv2.imshow("Output", output)
    #cv2.waitKey(0)

