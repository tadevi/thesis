import json

from bson import ObjectId
from flask import Flask, render_template, request

from modules import utils
from modules.utils import storage


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

    @_app.route('/camera', methods=['POST'])
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

    try:
        _app.run(host='localhost', port=4000, threaded=True)
    except:
        print('unable to open port')
