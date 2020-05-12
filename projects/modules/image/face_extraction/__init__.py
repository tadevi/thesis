import time
from typing import List

import face_recognition
from numpy.core.multiarray import ndarray

from modules.base import Map
from modules.utils import log

tag = "Face extraction"


class Main(Map):
    def __init__(self, configs):
        self.configs = configs

    # output: list of face locations
    def run(self, input: ndarray) -> List:
        start_time = time.time()
        face_locations = face_recognition.face_locations(input)
        end_time = time.time()

        if len(face_locations) > 0:
            log.v(tag, "in", "{:.2f}".format((end_time - start_time) * 1000), "(ms) extracted", len(face_locations),
                  "faces")
        return face_locations
