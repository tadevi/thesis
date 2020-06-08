import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import time
from threading import Timer
import cv2

import face_recognition
import pymongo

import numpy as np

from modules import utils
from modules.base import Filter
from modules.utils import log
from modules.utils import storage
from modules.network import Network

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
face_storage_path = os.path.join(parent_folder_path, "face_db")

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["cloud-db"]
collection = db["profile"]
cursor = collection.find({})

known_face_encodings = []
profiles = []
for profile in cursor:
    profiles.append(profile)

    face_path = os.path.join(face_storage_path, profile["id"] + ".jpg")
    face_array = face_recognition.load_image_file(face_path)
    known_face_encodings.append(face_recognition.face_encodings(face_array)[0])

tag = "Face recognition"
log.i(tag, "loaded all", len(known_face_encodings), "known faces")


class Main(Filter):
    DROP_FRAME = 1

    def __init__(self, configs: dict):
        self.configs = configs
        if configs.get("layer") == 2:
            self.network = Network({})
        else:
            self.storage = storage.Main({
                "mongo_url": configs.get("mongo_url"),
                "db_name": configs.get("db_name"),
                "col_name": configs.get("col_name"),
            })

        # format:
        # {
        #     "id"
        #     "name"
        #     "start_time" (ms from epoch)
        # }
        self.appearing_people = {}
        self.timers = {}

        self.face_locations = []
        self.face_encodings = []

        self.recognized_profile_indices = set()
        self.face_names = []
        self.process_frame = 1

    def run(self, input: np.ndarray):
        unrecognized_people_count = 0

        if self.process_frame == Main.DROP_FRAME:
            self.process_frame = 1
            start_time = time.time()
            self.face_locations = face_recognition.face_locations(input)
            self.face_encodings = face_recognition.face_encodings(input, self.face_locations)
            self.recognized_profile_indices.clear()
            self.face_names.clear()

            for face_encoding in self.face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = int(np.argmin(face_distances))
                if matches[best_match_index]:
                    name = profiles[best_match_index]["name"]
                    self.recognized_profile_indices.add(best_match_index)
                else:
                    name = "unknown"
                    unrecognized_people_count += 1
                self.face_names.append(name)

            recognized_profiles = {profiles[i]["id"]: profiles[i] for i in self.recognized_profile_indices}
            end_time = time.time()

            log.v(tag, "in", "{:.2f}".format((end_time - start_time) * 1000), "(ms) recognized",
                  len(recognized_profiles),
                  "people:",
                  [profile["name"] for profile_id, profile in recognized_profiles.items()])
            if unrecognized_people_count > 0:
                log.v(tag, "(WARNING)", unrecognized_people_count, "people not recognized")

            self.store_records(recognized_profiles)

        #self.process_frame += 1

        if self.configs.get("layer") == 3:
            draw_result_on_frame(input, self.face_locations, self.face_names)
        return unrecognized_people_count > 0

    def store_records(self, profiles: dict):
        for id, profile in profiles.items():
            if id not in self.appearing_people:
                self.appearing_people[id] = {
                    "id": id,
                    "name": profile["name"],
                    "start_time": utils.current_milli_time()
                }

            timer = self.timers.get(id)
            if timer is not None:
                timer.cancel()

            people = self.appearing_people[id]
            people["end_time"] = utils.current_milli_time()
            timer = Timer(5, self.store_record, args=(people,))
            self.timers[id] = timer
            timer.start()

    def store_record(self, record):
        if self.configs.get("layer") == 2:
            self.network.post(self.configs["cloud_url"] + "/appearance", record)
        else:
            self.storage.run(record)
        self.appearing_people.pop(record["id"], None)


def draw_result_on_frame(frame, face_locations: list, face_names):
    # Display the results
    frame = frame.copy()
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        # top *= 4
        # right *= 4
        # bottom *= 4
        # left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 28), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)
    return frame
