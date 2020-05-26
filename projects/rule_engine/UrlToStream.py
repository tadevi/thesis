from time import sleep

import youtube_dl
from cv2 import cv2
import pafy


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


def pafy_to_stream(url):
    video = pafy.new(url)
    cam = None
    for stream in video.streams:
        if stream.resolution == '640x360':
            url = stream.url
            cam = cv2.VideoCapture(url)
    return cam


class UrlToStream:
    DEFAULT_QUALITY = '360p'

    def __init__(self, configs):
        self.configs = configs
        self.init_cam()

    def init_cam(self):
        url = self.configs['url']
        if self.configs.get('demo'):
            self.cam = pafy_to_stream(url)
        else:
            self.cam = cv2.VideoCapture(url)

    def get(self):
        try:
            if self.configs.get('demo') and self.configs.get('sleep'):
                sleep(self.configs.get('sleep'))

            _, frame = self.cam.read()

            if frame is None and self.configs.get('demo'):
                self.init_cam()
                _, frame = self.cam.read()
            return frame
        except:
            return None
