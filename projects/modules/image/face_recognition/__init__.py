import os
import time
from typing import Dict

import face_recognition
import pymongo

import numpy as np

from modules.base import Map
from modules.storage import DEFAULT_MONGO_URL, DEFAULT_MONGO_DB
from modules.utils import log

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
face_storage_path = os.path.join(parent_folder_path, "face_db")

mongo_client = pymongo.MongoClient(DEFAULT_MONGO_URL)
db = mongo_client[DEFAULT_MONGO_DB]
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


class Main(Map):
    def __init__(self, configs):
        self.configs = configs

    # input:
    # {
    #     frame: ndarray,
    #     face_locations: list
    # }
    def run(self, input: Dict) -> (Dict[str, Dict], list):
        start_time = time.time()

        frame = input["frame"]
        face_locations = input["face_locations"]

        face_encodings = face_recognition.face_encodings(frame, face_locations)

        unrecognized_people_count = 0
        recognized_profile_indices = set()
        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = int(np.argmin(face_distances))
            if matches[best_match_index]:
                name = profiles[best_match_index]["name"]
                recognized_profile_indices.add(best_match_index)
            else:
                name = "unknown"
            face_names.append(name)

        recognized_profiles = {profiles[i]["id"]: profiles[i] for i in recognized_profile_indices}
        end_time = time.time()

        log.v(tag, "in", "{:.2f}".format((end_time - start_time) * 1000), "(ms) recognized", len(recognized_profiles),
              "people:",
              [profile["name"] for profile_id, profile in recognized_profiles.items()])
        if unrecognized_people_count > 0:
            log.v(tag, "(WARNING)", unrecognized_people_count, "people not recognized")

        return recognized_profiles, face_names
