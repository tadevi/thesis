import urllib.request
import cv2.cv2 as cv2
import numpy as np


class MjpegToStream:
    def __init__(self, configs):
        print('MJPEG TO STREAM')
        self.url = configs['url']
        self.stream = urllib.request.urlopen(self.url)

    def get(self):
        byte_arr = b''
        byte_arr += self.stream.read(1024)
        a = byte_arr.find(b'\xff\xd8')  # frame starting
        b = byte_arr.find(b'\xff\xd9')  # frame ending
        if a != -1 and b != -1:
            jpg = byte_arr[a:b + 2]
            byte_arr = byte_arr[b + 2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            return img
