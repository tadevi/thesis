from time import sleep

import youtube_dl
from cv2 import cv2


class UrlToStream:
    def __init__(self, configs):
        self.configs = configs
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
            return frame
        except:
            return None
