from cv2 import cv2

from modules.base import Map


class Main(Map):
    def __init__(self, configs):
        pass

    def run(self, input):
        cv2.imshow('frame', input)
        cv2.waitKey(1)
        return input
