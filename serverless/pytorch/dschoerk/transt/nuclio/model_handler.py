

import jsonpickle
import numpy as np
import torch
from pysot_toolkit.bbox import get_axis_aligned_bbox
from pysot_toolkit.trackers.net_wrappers import NetWithBackbone
from pysot_toolkit.trackers.tracker import Tracker
from PIL import Image
import os


pathToFolder = "/opt/nuclio/common/Folder3/"

class ModelHandler:
    def __init__(self):
        self.ind_of_dir = 1
        use_gpu = torch.cuda.is_available()
        net_path = '/transt.pth' # Absolute path of the model
        net = NetWithBackbone(net_path=net_path, use_gpu=use_gpu)
        self.tracker = Tracker(name='transt', net=net, window_penalty=0.49, exemplar_size=128, instance_size=256)

    def decode_state(self, state):
        self.tracker.net.net.zf = jsonpickle.decode(state['model.net.net.zf'])
        self.tracker.net.net.pos_template = jsonpickle.decode(state['model.net.net.pos_template'])

        self.tracker.window = jsonpickle.decode(state['model.window'])
        self.tracker.center_pos = jsonpickle.decode(state['model.center_pos'])
        self.tracker.size = jsonpickle.decode(state['model.size'])
        self.tracker.channel_average = jsonpickle.decode(state['model.channel_average'])
        self.tracker.mean = jsonpickle.decode(state['model.mean'])
        self.tracker.std = jsonpickle.decode(state['model.std'])
        self.tracker.inplace = jsonpickle.decode(state['model.inplace'])

        self.tracker.features_initialized = False
        if 'model.features_initialized' in state:
            self.tracker.features_initialized = jsonpickle.decode(state['model.features_initialized'])

    def encode_state(self):
        state = {}
        state['model.net.net.zf'] = jsonpickle.encode(self.tracker.net.net.zf)
        state['model.net.net.pos_template'] = jsonpickle.encode(self.tracker.net.net.pos_template)
        state['model.window'] = jsonpickle.encode(self.tracker.window)
        state['model.center_pos'] = jsonpickle.encode(self.tracker.center_pos)
        state['model.size'] = jsonpickle.encode(self.tracker.size)
        state['model.channel_average'] = jsonpickle.encode(self.tracker.channel_average)
        state['model.mean'] = jsonpickle.encode(self.tracker.mean)
        state['model.std'] = jsonpickle.encode(self.tracker.std)
        state['model.inplace'] = jsonpickle.encode(self.tracker.inplace)
        state['model.features_initialized'] = jsonpickle.encode(getattr(self.tracker, 'features_initialized', False))

        return state

    def init_tracker(self, img, bbox):
        cx, cy, w, h = get_axis_aligned_bbox(np.array(bbox))
        gt_bbox_ = [cx - w / 2, cy - h / 2, w, h]
        init_info = {'init_bbox': gt_bbox_}
        self.tracker.initialize(img, init_info)

        PIL_image = Image.fromarray(np.uint8(img)).convert('RGB')
        PIL_image.save(pathToFolder+'frame'+str(self.ind_of_dir)+'.jpg')

        f = open(pathToFolder+"init"+str(self.ind_of_dir)+".txt", "w+")
        f.write(str(cx-w/2)+" "+str(cy-h/2)+" "+str(cx+w/2)+" "+str(cy+h/2))
        f.close()
        self.ind_of_dir+=1

    def track(self, img):


        PIL_image = Image.fromarray(np.uint8(img)).convert('RGB')
        PIL_image.save(pathToFolder+'frame'+str(self.ind_of_dir)+'.jpg')

        f = open(pathToFolder+"track"+str(self.ind_of_dir)+".txt", "w+")
        f.write("track!")
        f.close()

        # ansPath = ""
        # if self.ind_of_dir == 2:
        #     ansPath = pathToFolder+"init"+str(1)+".txt"
        # else:
        #     ansPath = pathToFolder+"update"+str(self.ind_of_dir-1)+".txt"

        ansPath1 = pathToFolder+"update"+str(self.ind_of_dir-1)+".txt"
        ansPath2 = pathToFolder+"init"+str(self.ind_of_dir-1)+".txt"

        ansPath = ""

        while not (os.path.exists(ansPath1) or os.path.exists(ansPath2)):
            pass
        if (os.path.exists(ansPath1)):
            ansPath = ansPath1
        else:
            ansPath = ansPath2

        ansFile = open(ansPath, "r")
        ansStr = ansFile.read()
        l, t, r, b = [float(x) for x in ansStr.split(" ")]
        ansFile.close()


        self.ind_of_dir+=1
        return (l, t, r, b)

    def infer(self, image, shape, state):
        if state is None:
            init_shape = (shape[0], shape[1], shape[2] - shape[0], shape[3] - shape[1])

            self.init_tracker(image, init_shape)
            state = self.encode_state()
        else:
            self.decode_state(state)
            shape = self.track(image)
            state = self.encode_state()

        return shape, state
