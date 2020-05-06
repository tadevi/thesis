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

    # parent_folder_path = os.path.abspath(os.path.dirname(__file__))
    # parent_folder_path = os.path.join(parent_folder_path, "data")

    # human_path1 = os.path.join(parent_folder_path, "human1.jpg")
    # human_path2 = os.path.join(parent_folder_path, "human2.jpg")
    # no_human_path1 = os.path.join(parent_folder_path, "no_human1.jpg")
    # no_human_path2 = os.path.join(parent_folder_path, "no_human2.jpg")

    # 1280 x 720 resolution
    # human_img1 = cv2.imread(human_path1)
    # human_img2 = cv2.imread(human_path2)
    # no_human_img1 = cv2.imread(no_human_path1)
    # no_human_img2 = cv2.imread(no_human_path2)

    human_detection = human_detection.Main({})

    print("start running human detection")

    cap = cv2.VideoCapture(0)
    ret, input = cap.read()

    while input is not None:
        # human_detection.run(human_img1)
        # human_detection.run(human_img2)
        # human_detection.run(no_human_img1)
        # human_detection.run(no_human_img2)

        human_detection.run(input)
        ret, input = cap.read()
