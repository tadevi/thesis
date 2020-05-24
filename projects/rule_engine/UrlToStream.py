from time import sleep

import youtube_dl
from cv2 import cv2


class UrlToStream:
    def __init__(self, configs):
        self.configs = configs
        self.frame_counter = 0
        url = configs['url']
        if configs.get('demo'):
            ydl_opts = {}
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', None)
            for f in formats:
                if f.get('format_note', None) == '360p':
                    url = f.get('url', None)
                    self.cam = cv2.VideoCapture(url)
        else:
            self.cam = cv2.VideoCapture(url)

    def get(self):
        try:
            if self.configs.get('demo'):
                sleep(0.03)
            _, frame = self.cam.read()

            self.frame_counter += 1

            if self.frame_counter == self.cam.get(cv2.CAP_PROP_FRAME_COUNT):
                self.frame_counter = 0
                self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return frame
        except:
            return None
