from threading import Thread

from cv2 import cv2
from flask import *

from rule_engine import HandleStream, lookup_rule, HandleScalar

channel = {}


def add_to_channel(channel_id, queue):
    channel[channel_id] = queue


def make_web():
    _app = Flask(__name__, template_folder='.')

    @_app.route('/')
    def index():
        return render_template('index.html')

    '''
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
        Thread(target=HandleStream(configs).run, args=()).start()
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

    def emitFrame(frame):
        _, frame = cv2.imencode('.JPEG', frame)
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')

    def gen(channel_id):
        queue = channel[channel_id]
        while True:
            frame = queue.get()
            yield emitFrame(frame)

    @_app.route('/video')
    def video():
        channel_id = request.args.get('id')
        if not (channel.get(id) is None):
            return {
                "status": "success",
                "message": "Resource not found!"
            }
        return Response(gen(channel_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @_app.route('/services')
    def services():
        pass

    try:
        _app.run(host='localhost', port=3000, threaded=True)
    except:
        print('unable to open port')
