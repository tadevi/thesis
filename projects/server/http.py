import sys
import traceback
from threading import Thread

from cv2 import cv2
from flask import *

from modules.utils import get_configs
from rule_engine import HandleStream, lookup_rule, HandleScalar

channel_analysis = {}
channel_stream = {}

'''
                           Fog 1                  Fog 2                         Cloud
    Camera ------>      start_up --------------> analysis -------------------> analysis

'''


def add_to_channel_analysis(channel_id, queue):
    channel_analysis[channel_id] = queue


def add_to_channel_stream(channel_id, queue):
    channel_stream[channel_id] = queue


def start_camera_analysis(configs):
    Thread(target=HandleStream(configs).run, args=()).start()


def start_up():
    start_up_cam = get_configs('start_up')
    for cam in start_up_cam:
        configs = {
            **cam,
            **lookup_rule(cam)
        }

        start_camera_analysis(configs)


def make_web():
    _app = Flask(__name__, template_folder='.')

    @_app.route('/')
    def index():
        return render_template('index.html')

    '''
    Receive stream from camera or lower layer fog node to process
    json body request have format:
    {
        "name": <rule name>,
        "url" : <optional>, // rtsp/ mjpeg stream for video stream,
        ... additional fields
    }
    '''

    @_app.route('/stream/', methods=['POST'])
    def stream():
        data = request.json
        configs = lookup_rule(data)
        node_config = get_configs('meta')

        configs = {
            **configs,
            **node_config
        }
        start_camera_analysis(configs)
        return {
            "status": "success"
        }

    '''
    json body request have format:
    {
        "name": <rule name>,
        "data":{
            //body data for iot sensor
        }
    }
    '''

    @_app.route('/iot/', methods=['POST'])
    def iot_data():
        data = request.json
        configs = {
            'name': data['name']
        }
        inputs = data['data']

        configs = lookup_rule(configs)
        output = HandleScalar(configs).run(inputs)
        if output is None:
            return {
                "status": "failed",
                "data": "Invalid input"
            }
        else:
            return {
                "status": "success"
            }

    def gen(channel, channel_id):
        queue = channel[channel_id]
        while True:
            frame = queue.get()
            _, frame = cv2.imencode('.JPEG', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')

    '''
    Re-stream video from camera
    
    Choose between camera_video / proccessing stream
    '''

    @_app.route('/video')
    def video():
        if not (request.args.get('cam_id') is None):
            return Response(gen(channel_stream, request.args.get('cam_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        elif not (request.args.get('stream_id') is None):
            return Response(gen(channel_analysis, request.args.get('stream_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        return {
            "status": "success",
            "message": "Resource not found!"
        }

    '''
    fog node query
    '''

    @_app.route('/fog_meta')
    def fog_data():
        node_meta = get_configs('meta')
        return node_meta

    try:
        start_up()
        _app.run(host='localhost', port=3000, threaded=True)
    except:
        traceback.print_exc(file=sys.stdout)
