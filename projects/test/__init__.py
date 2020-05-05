def run():
    test_human_detection()


def test_validate_and_storage():
    from datetime import datetime
    from modules.text.gps import storage
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
    import os

    parent_folder_path = os.path.abspath(os.path.dirname(__file__))
    human_path = os.path.join(parent_folder_path, "human.jpg")
    no_human_path = os.path.join(parent_folder_path, "no_human.png")

    human_img = cv2.imread(human_path)
    no_human_img = cv2.imread(no_human_path)

    human_detection = human_detection.Main({})
    human_detection.run(human_img)
    human_detection.run(no_human_img)
