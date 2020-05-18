import os

import cv2

from modules import utils
from modules.utils import log

tag = "Test"

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
data_folder_path = os.path.join(parent_folder_path, "data")


def run():
    log.mode(log.LOG_MODE_INFO)

    # test_validate_and_storage()
    # test_human_detection()
    # test_camera_flow()
    # test_network()
    # test_cv2()
    # test_cloud_http()
    test_post_camera_cloud()


def test_validate_and_storage():
    from datetime import datetime
    from modules import storage
    from modules.text.gps import validate

    gps_data1 = {
        "device_id": 0,
        "longitude": 160,
        "latitude": 45,
        "speed": 30,
        "reliability": 0,
        "satellite": 0,
        "type": 3,
        "lock": 0,
        "datetime": datetime.now(),
        "option": None
    }

    gps_data2 = {
        "device_id": 0,
        "longitude": 160,
        "latitude": 45,
        "speed": -30,
        "reliability": 0,
        "satellite": 0,
        "type": 3,
        "lock": 0,
        "datetime": datetime.now(),
        "option": None
    }

    inputs = [gps_data1, gps_data2]

    configs = {
        "collection_name": "test"
    }

    validate = validate.Main({})
    storage = storage.Main(configs)

    for input in inputs:
        if validate.run(input):
            storage.run(input)


def test_human_detection():
    from modules.image import human_detection
    import cv2

    human_detection = human_detection.Main({})

    log.i(tag, "start running human detection")

    cap = cv2.VideoCapture(0)
    ret, input = cap.read()

    while input is not None:
        human_detection.run(input)
        ret, input = cap.read()


def test_camera_flow():
    import modules.image.human_detection as human_detection_pkg
    import modules.image.face_recognition as face_recognition_pkg
    import modules.image.face_extraction as face_extraction_pkg
    import modules.storage as storage_pkg
    import numpy as np

    human_detection_module = human_detection_pkg.Main({})
    face_extraction_module = face_extraction_pkg.Main({})
    face_recognition_module = face_recognition_pkg.Main({})
    storage_module = storage_pkg.Main({"collection_name": "appearance"})

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    # format:
    # {
    #     "id": ...,
    #     "name": ...,
    #     "start_time":... (ms from epoch)
    # }
    appearing_people = {}

    while frame is not None:
        # Resize frame of video to 1/4 size for faster face recognition processing
        input = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        input = np.array(input[:, :, ::-1])

        face_names = []

        if human_detection_module.run(input):
            face_locations = face_extraction_module.run(input)
            if len(face_locations) > 0:
                face_recognition_input = {
                    "frame": input,
                    "face_locations": face_locations
                }
                profiles, face_names = face_recognition_module.run(face_recognition_input)
            else:
                profiles = {}
        else:
            face_locations = []
            profiles = {}

        # update appearing list and insert new record to db if anyone disappear for at least 5s
        ids_to_remove = []
        for id, people in appearing_people.items():
            current_time = utils.current_milli_time()
            if id not in profiles:
                end_time = people.get("end_time")
                if end_time is not None:
                    if current_time - end_time > 5000:
                        new_record = people
                        log.i(tag, "New record:", new_record)

                        # insert record to database
                        storage_module.run(new_record)

                        ids_to_remove.append(id)
                else:
                    people["end_time"] = current_time
            else:
                people["end_time"] = None

        for id in ids_to_remove:
            appearing_people.pop(id, None)
        for id, profile in profiles.items():
            if id not in appearing_people:
                appearing_people[id] = {
                    "id": id,
                    "name": profile["name"],
                    "start_time": utils.current_milli_time()
                }

        # Display result
        display_result(frame, face_locations, face_names)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()


def display_result(frame, face_locations, face_names):
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)


def test_network():
    from protocols.http import make_web
    import threading

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    from modules import network
    network_module = network.Main({})

    is_post = True

    while True:
        if is_post:
            input("Press Enter to send POST\n")
            network_module.post("http://localhost:3000/iot",
                                {
                                    "name": "gps",
                                    "data": {
                                        "longitude": 180,
                                        "latitude": 60,
                                        "speed": 40,
                                        "datetime": utils.current_milli_time()
                                    }
                                })
        else:
            input("Press Enter to send GET\n")
            network_module.get("http://localhost:3000/video")
        is_post = not is_post


def test_cloud_http():
    from server.cloud_http import make_web
    import threading

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    from modules import network
    network_module = network.Main({})

    while True:
        input("Press Enter to send GET\n")
        network_module.get("http://localhost:4000/appearance",
                           {
                               "from": 1589197615040,
                               "to": 1589712007301
                           })


def test_post_camera_cloud():
    from server.cloud_http import make_web
    import threading

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    from modules import network
    network_module = network.Main({})

    while True:
        input("Press Enter to send POST\n")
        network_module.post("http://localhost:4000/camera",
                            {
                                "camera_id": "test",
                                "name": "cameraTest",
                                "type": -1,
                                "url": "https://google.com.vn"
                            })
