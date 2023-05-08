
import requests
import shutil
import pathlib
import os
import time
import json
import base64
from io import BytesIO
from PIL import Image

print("RUN!")


path = "serverless/common/Folder3"
mydir = pathlib.Path(path)
isExist = os.path.exists(path)
currentIndex = 1

if isExist:
    shutil.rmtree(mydir)
os.mkdir(path)


def get_current_image():
    img = Image.open(path + '/frame' + str(currentIndex) + '.jpg')
    im_file = BytesIO()
    img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    im_b64 = base64.b64encode(im_bytes).decode('utf-8')
    return im_b64

def init_request(x,y,w,h):

    data = {'init': 1, 'image': get_current_image(), 'x': x, 'y': y, 'y1': h, 'x1': w}
    headers = {'Content-type': 'application/json'}
    url = "http://0.0.0.0:8083"
    requests.post(url, json=data, headers=headers)


def track_request():
    data = {'image': get_current_image()}
    url = "http://0.0.0.0:8083"
    r = requests.get(url, json=data)
    print(r.json())
    json = r.json()
    return [str(json["x"]), str(json["y"]), str(json["width"]+json["x"]), str(json["height"]+json["y"])]

def react_on_init():
    time.sleep(0.001)
    print("init"+str(currentIndex))
    filename = path+"/init"+str(currentIndex)+".txt"
    f1 = open(filename, "r")
    initStr = f1.read()
    x, y, w, h = [float(x) for x in initStr.split(' ')]
    f1.close()
    reactname = path + "/inited" + str(currentIndex) + ".txt"
    f = open(reactname, "w+")
    f.close()
    print(x, y, w, h)
    init_request(x, y, w, h)

def react_on_track():
    print("track"+str(currentIndex))
    reactname = path + "/update" + str(currentIndex) + ".txt"
    f = open(reactname, "w+")
    new_coords = " ".join(track_request())
    print(new_coords)
    # f.write(f"200 200 300 {300+currentIndex*10}")
    f.write(new_coords)
    f.close()
    track_request()


def react_on_image():
    answered = False
    while not answered:
        if os.path.exists(path+"/init"+str(currentIndex)+".txt"):
            react_on_init()
            answered = True
        if os.path.exists(path+"/track"+str(currentIndex)+".txt"):
            react_on_track()
            answered = True


while True:
    if os.path.exists(path+"/frame"+str(currentIndex)+".jpg"):
        time.sleep(0.001)
        react_on_image()
        currentIndex+=1



