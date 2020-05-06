from cv2 import cv2


class Main:
    def __init__(self, configs):
        self.configs = configs
        self.video_capture = cv2.VideoCapture(configs['url'])

    def run(self, callback):
        print('Module already run with callback ', callback)
        while True:
            ret, frame = self.video_capture.read()
            callback(frame)
            cv2.waitKey(50)
