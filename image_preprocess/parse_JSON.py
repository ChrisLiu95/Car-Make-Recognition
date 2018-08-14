import json
import sys
import urllib.request
import time

def save_img(img_url, file_path):
	urllib.request.urlretrieve(img_url, file_path)

start = time.time()
with open('ferrari.json', 'r') as f:
	obj = json.load(f)
	res = []
	index = 0
	for item in obj['response']['docs']:
		try:
			if item["products_|UCI|#photo_|large-vehicle-photo-urls|"]:
				for url in item["products_|UCI|#photo_|large-vehicle-photo-urls|"].split("|"):
					try:
						save_img(url, "imgs/Ferrari/%s.jpg" % index)
						index += 1
						res.append(url)
					except:
						print("some error, who cares!")
						print(url)
		except:
			print("key error, nobody cares!")
	print("Mission completed! " + str(index) + " images has been downloaded.")
	print("time: " + str(time.time() - start) + "s")


