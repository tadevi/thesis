import os

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
data_folder_path = os.path.join(parent_folder_path, "data")


def run():
    # test_validate_and_storage()
    # test_human_detection()
    test_camera_flow()


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

    human_detection = human_detection.Main({})

    print("start running human detection")

    cap = cv2.VideoCapture(0)
    ret, input = cap.read()

    while input is not None:
        human_detection.run(input)
        ret, input = cap.read()


def test_camera_flow():
    import modules.image.human_detection as human_detection_pkg
    import modules.image.face_recognition as face_recognition_pkg
    import modules.image.face_extraction as face_extraction_pkg
    import cv2

    human_detection_module = human_detection_pkg.Main({})
    face_extraction_module = face_extraction_pkg.Main({})
    face_recognition_module = face_recognition_pkg.Main({})

    cap = cv2.VideoCapture(0)
    ret, input = cap.read()

    while input is not None:
        # Resize frame of video to 1/4 size for faster face recognition processing
        input = cv2.resize(input, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        input = input[:, :, ::-1]

        if human_detection_module.run(input):
            face_locations = face_extraction_module.run(input)
            if len(face_locations) > 0:
                face_recognition_input = {
                    "frame": input,
                    "face_locations": face_locations
                }
                face_recognition_module.run(face_recognition_input)

        ret, input = cap.read()
