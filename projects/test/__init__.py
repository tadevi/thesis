import os

from cv2 import cv2

from modules import log, utils, network

tag = "Test"

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
data_folder_path = os.path.join(parent_folder_path, "data")


def run():
    log.mode(log.LOG_MODE_VERBOSE)

    # test_validate_and_storage()
    # test_human_detection()
    # test_camera_flow()
    # test_network()
    # test_cv2()
    # test_cloud_http()
    # test_post_camera_cloud()
    # test_camera_flow()
    # test_post_fake_data()
    # test_fog1_stream()
    test_traffic_violation()


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
    import numpy as np

    human_detection_module = human_detection_pkg.Main({})
    face_recognition_module = face_recognition_pkg.Main({
        "col_name": "appearance"
    })

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    while frame is not None:
        # Resize frame of video to 1/4 size for faster face recognition processing
        input = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        input = np.array(input[:, :, ::-1])

        if human_detection_module.run(input):
            face_recognition_module.run(input)

        cv2.imshow('Video', input)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()


def test_gps_flow():
    from server.fog_http import make_web
    import threading
    from modules.network import Network
    from modules import utils

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    is_post = True

    while True:
        if is_post:
            input("Press Enter to send POST\n")
            Network.instance().post("http://localhost:3000/iot",
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
            Network.instance().get("http://localhost:3000/video")
        is_post = not is_post


def test_cloud_http():
    from server.cloud_http import make_web
    import threading
    from modules.network import Network

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    while True:
        input("Press Enter to send GET\n")
        Network.instance().get("http://localhost:4000/appearance",
                           {
                               "from": 1589197615040,
                               "to": 1589712007301
                           })


def test_post_camera_cloud():
    from server.cloud_http import make_web
    import threading
    from modules.network import Network

    t = threading.Thread(target=make_web)
    t.daemon = True
    t.start()

    while True:
        input("Press Enter to send POST\n")
        Network.instance().post("http://localhost:4000/camera",
                            {
                                "camera_id": "test",
                                "name": "cameraTest",
                                "type": -1,
                                "url": "https://google.com.vn"
                            })


def test_post_fake_data():
    from fake_data import fake_gps
    from fake_data import fake_water
    from server.fog_http import make_web
    import threading

    t = threading.Thread(target=make_web)
    t.start()

    input('ENTER to start posting fake text data to fog1\n')
    fog1_url = "http://0.0.0.0:3000"
    fake_gps = fake_gps.GpsDataFaker(fog1_url)
    fake_water = fake_water.WaterDataFaker(fog1_url)

    fake_gps.start_posting_fake_data()
    fake_water.start_posting_fake_data()


def test_fog1_stream():
    from server.fog_http import make_web
    import threading
    from modules.network import Network

    t = threading.Thread(target=make_web)
    t.start()

    input("ENTER to post stream meta to fog1\n")
    Network.instance().post("http://localhost:3000/stream/",
                        {
                            "name": "traffic_camera",
                            "camera_id": "0",
                            "url": 0
                        })


# def test_traffic_violation():
#     from modules.image.violation_detection.TrafficProcessor import TrafficProcessor
#     tp = TrafficProcessor()
#
#     cap = cv2.VideoCapture('video7.mp4')
#     while True:
#         _, frame = cap.read()
#         if frame is None:
#             cap = cv2.VideoCapture('video7.mp4')
#             continue
#         res = tp.cross_violation(frame)
#         print("reference:", res.get('reference'))
#         print("list_of_cars:", res.get('list_of_cars'))
#         print("cnt:", res.get('cnt'), '\n')
#         frame = res.get('frame')
#         cv2.imshow('Traffic Violation', frame)
#         cv2.waitKey(int(1/cap.get(cv2.CAP_PROP_FPS)*1000))


if __name__ == '__main__':
    cap = cv2.VideoCapture('video7.mp4')
    _, input = cap.read()
    imencoded = cv2.imencode(".jpg", input)[1]

    timestamp = utils.current_milli_time()
    file = {'file': (
    'cam{}_{}.jpg'.format(1, timestamp), imencoded.tostring(), 'image/jpeg', {'Expires': '0'})}
    data = {"timestamp": timestamp}
    network.Network.instance().post(
        'http://localhost:5000' + '/camera_capture',
        files=file, data=data, timeout=5, threading=False
    )