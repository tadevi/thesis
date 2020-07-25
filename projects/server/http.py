from cv2 import cv2
from flask import *

from data_dispatcher import DataDispatcher
from resource_manager.GlobalConfigs import GlobalConfigs
from server.channel import get_channel

tag = "Http"


def start_up():
    start_ups = GlobalConfigs.instance().get_config('start_up')
    for data in start_ups:
        DataDispatcher.instance().dispatch(data)


app = Flask(__name__)


@app.route('/')
def index():
    return "..."


@app.route('/iot/', methods=['POST'])
@app.route('/stream/', methods=['POST'])
def stream():
    data = request.json
    DataDispatcher.instance().dispatch(data)
    return {
        "status_code": 200,
        "message": "Server received your request!"
    }


def gen(channel, channel_id):
    queue = channel.get(channel_id)
    if queue is not None:
        while True:
            frame = queue.get()
            _, frame = cv2.imencode('.JPEG', frame)
            yield (b'--frame\r\n'
                   b'Content-Type:image/jpeg\r\n'
                   b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                                                                    b'\r\n' + frame.tostring() + b'\r\n')
            # time.sleep(GlobalConfigs.instance().FPS)
    else:
        yield b'--\r\n'


'''
Re-stream video from camera

Choose between camera_video / proccessing stream
'''


@app.route('/video')
def video():
    if request.args.get('analysis_id') is not None:
        return Response(gen(get_channel('analysis'), request.args.get('analysis_id')),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    elif request.args.get('stream_id') is not None:
        return Response(gen(get_channel('stream'), request.args.get('stream_id')),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


'''
fog node query
'''


@app.route('/fog_meta')
def fog_meta():
    node_meta = GlobalConfigs.instance().get_config('meta')
    return node_meta


@app.route('/request_update', methods=['POST'])
def request_update():
    GlobalConfigs.instance().check_for_update()
    return {
        "status_code": 200,
        "message": "Server received your request!"
    }


def make_web():
    start_up()
    app.run(host='0.0.0.0', port=GlobalConfigs.instance().get_port(), threaded=True)
