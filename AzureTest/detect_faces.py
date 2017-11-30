########### Python 3.6 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64, requests, json
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import io
from time import sleep

###############################################
#### Update or verify the following values. ###
###############################################

#image URL
URL = 'http://www.choruscallasia.com/management/wp-content/themes/cca2017/images/service/video/serv-mainImage.jpg'

# Replace the subscription_key string value with your valid subscription key.
subscription_key = '5b7814fd8bd54577b90fad094c8503f0'

# Replace or verify the region.
#
# You must use the same region in your REST API call as you used to obtain your subscription keys.
# For example, if you obtained your subscription keys from the westus region, replace
# "westcentralus" in the URI below with "westus".
#
# NOTE: Free trial subscription keys are generated in the westcentralus region, so if you are using
# a free trial subscription key, you should not need to change this region.
uri_base = 'https://westcentralus.api.cognitive.microsoft.com'

# Request headers.
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

# Request parameters.
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
}

# Body. The URL of a JPEG image to analyze.
body = {'url': URL}


try:
    # Execute the REST API call and get the response.
    response = requests.request('POST', uri_base + '/face/v1.0/detect', json=body, data=None, headers=headers, params=params)

    print ('Response:')
    parsed = json.loads(response.text)
    print (json.dumps(parsed, sort_keys=True, indent=2))



except Exception as e:
    print('Error:')
    print(e)

####################################

with urllib.request.urlopen(URL) as url:
    f = io.BytesIO(url.read())

img = np.array(Image.open(f))

for key in parsed:
    height = key["faceRectangle"]["height"]
    left = key["faceRectangle"]["left"]
    top = key["faceRectangle"]["top"]
    width = key["faceRectangle"]["width"]
    plt.plot( [left, left+width], [top, top], 'r', lw=2 )
    plt.plot( [left+width, left+width], [top, top+height], 'r', lw=2 )
    plt.plot( [left+width, left], [top+height, top+height], 'r', lw=2 )
    plt.plot( [left, left], [top+height, top], 'r', lw=2 )

plt.imshow(img)
plt.show()
