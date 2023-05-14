
import base64
import io
import json
import requests
from io import BytesIO
import base64
import subprocess
import numpy as np
from PIL import Image



f=open("/opt/nuclio/common/ip.txt", "r")
ip=f.read()
f.close()
url = 'http://'+ip+':8083'


def image_to_base64(img):
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    im_b64 = base64.b64encode(im_bytes).decode('utf-8')
    return im_b64


def init_context(context):
    context.logger.info("Init context...  0%")
    context.logger.info("Init context...100%")

def handler(context, event):

    data = event.body
    buf = io.BytesIO(base64.b64decode(data["image"]))
    shapes = data.get("shapes")
    states = data.get("states")

    image = Image.open(buf).convert('RGB')
    shape = shapes[0]
    data = {'image': image_to_base64(image), 'x': shape[0], 'y': shape[1], 'x1': shape[2], 'y1': shape[3]}

    results={}
    if len(states) == 0:
        requests.post(url, json=data)

        results = {
            'shapes': [shape],
            'states': []
        }
    else:
        r = requests.get(url, json=data)
        j = r.json()
        x=j["x"]
        y=j["y"]
        width=j['width']
        height=j['height']
        results = {
            'shapes': [[x,y,x+width,y+height]],
            'states': []
        }
    return context.Response(body=json.dumps(results), headers={},
        content_type='application/json', status_code=200)
