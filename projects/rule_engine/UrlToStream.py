import traceback

import pafy
import youtube_dl
from cv2 import cv2

from modules import log
from resource_manager.GlobalConfigs import GlobalConfigs

TOTAL_DATA = 0
LAST_TOTAL_PRINTED = 0


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
            self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 0)

    def get(self):
        global TOTAL_DATA
        global LAST_TOTAL_PRINTED
        try:
            _, frame = self.cam.read()

            if frame is not None:
                height, width, depth = frame.shape
                TOTAL_DATA += height * width * depth
            else:
                cur_total = TOTAL_DATA / (1024 * 1024)
                if cur_total != LAST_TOTAL_PRINTED:
                    LAST_TOTAL_PRINTED = cur_total
                    print("Handled total", "{:.2f}".format(LAST_TOTAL_PRINTED), "(MB) data")

                self.init_cam()
                return self.get()

            return frame
        except:
            log.e('UrlToStream', traceback.format_exc())
            return None
