from threading import Thread

import cv2
from flask import *

from rule_engine import HandleStream, lookup_rule, HandleScalar


def make_web():
    app = Flask(__name__, template_folder='.')

    @app.route('/')
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

    @app.route('/stream/', methods=['POST'])
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

    @app.route('/iot/', methods=['POST'])
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

    @app.route('/video')
    def video():
        id=request.args.get('id')
        return {
            "status":"success",
            "id": id
        }

    try:
        app.run(host='localhost', port=3000, threaded=True)
    except:
        print('unable to open port')
