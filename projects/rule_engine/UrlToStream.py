from time import sleep

import youtube_dl
from cv2 import cv2


def youtube_to_stream(url):
    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(url, download=False)
    formats = info_dict.get('formats', None)
    cam = None
    for f in formats:
        if f.get('format_note', None) == UrlToStream.DEFAULT_QUALITY:
            url = f.get('url', None)
            cam = cv2.VideoCapture(url)
    return cam


class UrlToStream:
    DEFAULT_QUALITY = '360p'

    def __init__(self, configs):
        self.configs = configs

        self.frame_counter = 0

        url = configs['url']
        if configs.get('demo'):
            self.cam = youtube_to_stream(url)
        else:
            self.cam = cv2.VideoCapture(url)

    def get(self):
        try:
            if self.configs.get('demo') and self.configs.get('sleep'):
                sleep(self.configs.get('sleep'))

            _, frame = self.cam.read()

            self.frame_counter += 1

            if self.frame_counter == self.cam.get(cv2.CAP_PROP_FRAME_COUNT):
                self.frame_counter = 0
                self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return frame
        except:
            return None
