import requests
import json
import cv2
import time
from threading import Thread



def test():
	imagelist=["apple.jpeg","tomato2.jpeg","mango.jpeg","tomato.jpeg","apple2.jpeg"]
	counter=0
	start_time=time.time()
	for i in range(10):
		for imgs in imagelist:
			addr = 'http://app-hyperpigmented-strontian.mybluemix.net'
			test_url = addr + '/api/test'

			# prepare headers for http request
			content_type = 'image/jpeg'
			headers = {'content-type': content_type}

			img = cv2.imread(imgs)
			# encode image as jpeg
			_, img_encoded = cv2.imencode('.jpg', img)
			# send http request with image and receive response
			start=time.time()

			response = requests.post(test_url, data=img_encoded.tostring(), headers=headers)
			end=(time.time()-start,1)
			# decode response
			#print (json.loads(response.text))
			counter=counter+1
	end_time=time.time()
	duration= round((end_time- start_time)/counter,2)
	print(str(duration)+" seconds per sample " +str(counter)+" Samples")

# expected output: {u'message': u'image received. size=124x124'}
print ("Five Clients request concurrenttly ")
thread1 = Thread(target = test)
thread2 = Thread(target = test)
thread3 = Thread(target = test)
thread4 = Thread(target = test)
thread5 = Thread(target = test)

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

