from cv2 import cv2


class UrlToStream:
    def __init__(self, configs):
        url = configs['url']
        self.cam = cv2.VideoCapture(url)

    def get(self):
        _, frame = self.cam.read()

        return frame
