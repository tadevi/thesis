import json

from bson import ObjectId
from cv2 import cv2
from flask import Flask, render_template, request, Response

from modules import utils
from modules.utils import storage, get_configs, lookup_rule
from server.channel import get_channel
from server.http import start_camera_analysis


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return o


encoder = JSONEncoder()

config_name = 'config/config.json'


def get_database():
    with open(config_name, 'r') as f:
        json_config = json.load(f)
        db_config = json_config['database']

        return storage.Main(db_config)


def make_web():
    _app = Flask(__name__, template_folder='.')
    database = get_database()

    @_app.route('/')
    def index():
        return render_template('index.html')

    '''
    ai services
    '''

    @_app.route('/appearance')
    def get_people():
        from_time = request.args.get('from')
        if from_time is not None:
            try:
                from_time = int(from_time)
            except:
                return {"data": []}
        else:
            from_time = 0

        end_time = request.args.get('to')
        if end_time is not None:
            try:
                end_time = int(end_time)
            except:
                return {"data": []}
        else:
            end_time = utils.current_milli_time()

        cursor = database.find_many('appearance',
                                    {'$or': [
                                        {'start_time': {
                                            '$gte': from_time,
                                            '$lte': end_time,
                                        }},
                                        {'end_time': {
                                            '$gte': from_time,
                                            '$lte': end_time,
                                        }},
                                    ]})

        return {"data": [utils.json_encode(document) for document in cursor]}

    '''
    camera services
    '''

    @_app.route('/camera', methods=['GET'])
    def get_camera():
        camera_id = request.args.get('id')

        if camera_id is not None:
            data = database.find_one('camera', {'camera_id': str(camera_id)})
            data = utils.json_encode(data) if data is not None else {}
        else:
            cursor = database.find_many('camera', {})
            data = [utils.json_encode(document) for document in cursor]

        return {"data": data}

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
        else:
            yield b'--\r\n'

    @_app.route('/video')
    def video():
        if request.args.get('analysis_id') is not None:
            return Response(gen(get_channel('analysis'), request.args.get('analysis_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        elif request.args.get('stream_id') is not None:
            return Response(gen(get_channel('stream'), request.args.get('stream_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

    @_app.route('/camera/', methods=['POST'])
    def add_camera():
        json = request.json
        database.insert_one('camera', json)
        return {
            "status": "success"
        }

    '''
    iot services
    '''

    @_app.route('/traffic', methods=['GET'])
    def get_predict_traffic():
        pass

    meta = get_configs('meta')
    _app.run(host='0.0.0.0', port=meta['port'], threaded=True)
