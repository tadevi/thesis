import sys
import traceback
from threading import Thread

from cv2 import cv2
from flask import *

from modules.utils import get_configs, log
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
    log.i('starting a camera with configs', configs)
    Thread(target=HandleStream(configs).run, args=()).start()


def start_up():
    start_up_cam = get_configs('start_up')
    for cam in start_up_cam:
        configs = lookup_rule(cam)
        configs['camera_id'] = cam['camera_id']
        configs['name'] = cam['name']
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
        "camera_id":<camera id>,
        "url" : <optional>, // rtsp/ mjpeg stream for video stream,
        ... additional fields
    }
    '''

    @_app.route('/stream/', methods=['POST'])
    def stream():
        data = request.json
        configs = lookup_rule(data)
        configs['camera_id'] = data['camera_id']
        configs['name'] = data['name']
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
            return Response(gen(channel_analysis, request.args.get('cam_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        elif not (request.args.get('stream_id') is None):
            return Response(gen(channel_stream, request.args.get('stream_id')),
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
        meta=get_configs('meta')
        start_up()
        _app.run(host='0.0.0.0', port=meta['port'], threaded=True)
    except:
        traceback.print_exc(file=sys.stdout)
