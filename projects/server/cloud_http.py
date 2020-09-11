import json
import os
from functools import reduce
from pathlib import Path
from time import sleep

import pymongo
from bson import ObjectId
from cv2 import cv2
from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for, make_response, \
    send_file
from flask_login import login_user, logout_user, current_user, login_required, UserMixin, LoginManager
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from data_dispatcher import DataDispatcher
from data_dispatcher.UrlToStream import pafy_to_stream
from modules import utils, storage, log
from resource_manager.GlobalConfigs import GlobalConfigs
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask
from server.channel import get_channel
from flask_socketio import SocketIO

tag = 'CLOUD HTTP'


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return o


encoder = JSONEncoder()

last_post_time = None


def get_database():
    return storage.Main(GlobalConfigs.instance().get_config('database'))


def make_web():
    app = Flask(__name__, template_folder='.')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    database = get_database()
    lm = LoginManager()  # flask-loginmanager
    lm.init_app(app)  # init the login manager
    app.debug = True
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # provide login manager with load_user callback
    @lm.user_loader
    def load_user(user_id):
        return User('mgt', '12345678')

    # @app.after_request
    # def apply_caching(resp):
    #     resp.headers['Access-Control-Allow-Origin'] = '*'
    #     resp.headers['Access-Control-Allow-Methods'] = '*'
    #     resp.headers['Access-Control-Allow-Domain'] = '*'
    #     resp.headers['Access-Control-Allow-Credentials'] = True
    #     return resp

    # App main route + generic routing
    @app.route('/', defaults={'path': 'notifications.html'})
    @app.route('/<path>')
    def index(path):
        if not current_user.is_authenticated:
            # test
            user = User("mgt", "12345678")
            login_user(user)

            # return redirect(url_for('login'))

        try:

            # try to match the pages defined in -> pages/<input file>
            return render_template('templates/layouts/default.html',
                                   content=render_template('templates/pages/' + path))
        except:

            return render_template('templates/layouts/default.html',
                                   content=render_template('templates/pages/notifications.html'))

    '''
    ai services
    '''

    '''
    air
    '''

    @app.route('/iot/', methods=['POST'])
    def iot():
        data = request.json
        on_new_iot_record(data)
        return {
            "status_code": 200,
            "message": "Server received your request!"
        }

    def on_new_iot_record(data):
        event_args = data['data']
        event_name = "iot/" + data['name'] + '/' + event_args['district']

        log.v(tag, "Emitted topic:", event_name, "with data:", event_args)

        socketio.emit(event_name, event_args)

        database.insert_one(data['name'], data['data'])

        if data['name'] == 'air':
            cursor = database.db[data['name']].find({}).sort("timestamp", pymongo.DESCENDING).limit(20)
            records = []
            for record in cursor:
                records.append(utils.json_encode(record))
            records.append(event_args)
            avg = round(reduce(lambda x, y: x + y['pm25'], records, 0) / len(records), 2)

            if avg < 150:
                type = 'warning'
                eval = "Unhealthy"
            elif avg < 200:
                type = 'warning'
                eval = "Harmful"
            elif avg < 300:
                type = 'primary'
                eval = "Very harmful"
            else:
                type = 'danger'
                eval = "Dangerous"

            global last_post_time

            cur_time = utils.current_milli_time()
            if avg >= 100 and (last_post_time is None or cur_time - last_post_time > 10000):
                noti = {
                    'timestamp': utils.current_milli_time(),
                    'type': type,
                    'message': 'At {}, average PM2.5 value of whole city is {}, which is evaluated as <b>{}</b>'.format(
                        utils.get_time_formatted(event_args['timestamp']),
                        avg,
                        eval
                    )
                }
                database.insert_one('notification', utils.json_encode(noti))
                socketio.emit("notification", utils.json_encode(noti))
                last_post_time = cur_time


    @app.route('/iot/', methods=['GET'])
    def get_iot():
        col_name = request.args.get('name')
        district = request.args.get('district')
        cursor = database.db[col_name].find({'district': district}).sort("timestamp", pymongo.DESCENDING).limit(20)
        res = []
        for record in cursor:
            res.append(utils.json_encode(record))
        return {
            'data': res
        }

    @app.route('/iot_locations', methods=['GET'])
    def get_iot_locations():
        return {
            'data': [
                'Thu Duc',
                'Binh Thanh',
                'Tan Binh',
                'District 1',
                'District 2',
                'District 3',
                'District 4',
                'District 5',
                'District 6',
                'District 7',
                'District 8',
                'District 9',
                'District 10',
                'District 11',
                'District 12',
            ]
        }

    @socketio.on('my event')
    def handle_my_custom_event(json):
        log.v(tag, 'received json:', json)

    cameras = {}

    @app.route('/cameras', methods=['POST', 'GET'])
    def camera():
        if request.method == 'POST':
            json = request.json

            # database.upsert_one('camera', json, {'camera_id': json.get('camera_id')})
            cameras[json.get('camera_id')] = json

            on_new_camera(json)
            return {
                "status": "success"
            }
        elif request.method == 'GET':
            camera_id = request.args.get('id')

            if camera_id is not None:
                # data = database.find_one('camera', {'camera_id': str(camera_id)})
                data = cameras[str(camera_id)]

                data = utils.json_encode(data) if data is not None else {}
            else:
                # cursor = database.find_many('camera', {})
                # data = [utils.json_encode(document) for document in cursor]
                data = list(cameras.values())

            return {"data": data}

    def on_new_camera(camera):
        event_name = "new camera"
        log.v(tag, "Emitted topic:", event_name, "with data:", camera)

        socketio.emit(event_name, camera)

        noti = {
            'timestamp': utils.current_milli_time(),
            'type': 'info',
            'message': 'At {}, camera with ID <b>{}</b> has connected to system'.format(
                utils.get_time_formatted(utils.current_milli_time()),
                camera['camera_id']
            )
        }
        database.insert_one('notification', utils.json_encode(noti))
        socketio.emit("notification", utils.json_encode(noti))

    '''
    ai services
    '''

    @app.route('/violation', methods=['POST'])
    def store_violation():
        record = {
            'timestamp': request.form.get('timestamp'),
            'camera_id': request.form.get('camera_id'),
            'type': request.form.get('type')
        }
        database.insert_one('violation', record)
        f = request.files['file']
        Path(GlobalConfigs.instance().project_root + "/violation").mkdir(parents=True, exist_ok=True)
        f.save('violation/' + secure_filename(f.filename))
        on_new_violation_record(record)
        return {
            "status_code": 200,
            "message": "Server received your request!"
        }

    def on_new_violation_record(violation):
        event_name = "violation/cam" + violation['camera_id']
        violation['evidence'] = 'http://{}:{}/evidence?camera_id={}&timestamp={}'.format(
            GlobalConfigs.instance().get_node_ip(),
            GlobalConfigs.instance().get_port(),
            violation['camera_id'],
            violation['timestamp']
        )
        log.v(tag, "Emitted topic:", event_name, "with data:", violation)
        socketio.emit(event_name, utils.json_encode(violation))

    @app.route('/violation', methods=['GET'])
    def get_violations():
        cursor = database.db['violation'].find({'camera_id': request.args.get('camera_id')}).sort("timestamp",
                                                                                                  pymongo.DESCENDING).limit(
            20)
        res = []
        for record in cursor:
            record['evidence'] = 'http://{}:{}/evidence?camera_id={}&timestamp={}'.format(
                GlobalConfigs.instance().get_node_ip(),
                GlobalConfigs.instance().get_port(),
                record['camera_id'],
                record['timestamp']
            )
            res.append(utils.json_encode(record))
        return {
            'data': res
        }

    @app.route('/evidence', methods=['GET'])
    def get_evidence():
        return send_file(
            '{}/violation/cam{}_{}.jpg'.format(
                GlobalConfigs.instance().project_root,
                request.args.get('camera_id'),
                request.args.get('timestamp')
            ),
            mimetype='image/jpg')

    @app.route('/notifications', methods=['GET'])
    def get_notifications():
        cursor = database.db['notification'].find({}).sort("timestamp", pymongo.DESCENDING).limit(20)
        res = []
        for record in cursor:
            res.append(utils.json_encode(record))
        return {
            'data': res
        }

    @app.route('/config', methods=['GET'])
    def get_config():
        layer = request.args.get('layer')
        position = request.args.get('position')
        ip = request.args.get('ip')
        port = request.args.get('port')

        if None not in [layer, position, ip, port]:
            nodes_ip = GlobalConfigs.instance().nodes_ip.get("layers")
            layer_ips = nodes_ip[layer]

            layer = int(layer)
            position = int(position)
            port = int(port)

            # if all((ip_port['ip'] != ip or ip_port['port'] != port for ip_port in layer_ips)):
            #     layer_ips.append({
            #         'ip': ip,
            #         'port': port
            #     })
            #     log.v(tag, "added a new node at layer", layer, ", position", position, "with ip:", ip, ", port:",
            #           port)

            layer1_count = len(nodes_ip.get("1"))
            layer2_count = len(nodes_ip.get("2"))
            cloud_ip = nodes_ip.get("cloud").get("ip")
            cloud_port = nodes_ip.get("cloud").get("port")

            if layer == 1:
                index = int((position - 1) / (layer1_count / layer2_count))
                fog2_ip = nodes_ip.get("2")[index].get("ip")
                fog2_port = nodes_ip.get("2")[index].get("port")
                config = GlobalConfigs.instance().get_fog1_config(cloud_ip, cloud_port, fog2_ip, fog2_port)
            else:  # = 2
                config = GlobalConfigs.instance().get_fog2_config(cloud_ip, cloud_port)

            return config

        else:
            return {}

    @app.route('/node_id', methods=['GET'])
    def get_node_id():
        ip = request.args.get('ip')
        port = request.args.get('port')

        if None not in [ip, port]:
            nodes_ip = GlobalConfigs.instance().nodes_ip.get("layers")
            for layer, layer_ips in nodes_ip.items():
                if layer != "cloud":
                    for idx, ip_port in enumerate(layer_ips):
                        if (ip == ip_port.get('ip') or GlobalConfigs.instance().test_on_local) and port == ip_port.get(
                                'port'):
                            id = str(layer) + '.' + str(idx + 1)
                            return {
                                'id': id
                            }
        return {}

    @app.route('/last_update', methods=['GET'])
    def get_last_update():
        return {
            "last_update_time": GlobalConfigs.instance().last_update_time
        }

    @app.route('/update', methods=['GET'])
    def get_update():
        project_root = GlobalConfigs.instance().project_root
        GlobalConfigs.instance().gen_update()
        response = send_from_directory(directory=project_root, filename='modules.zip')
        response.headers['last_update_time'] = GlobalConfigs.instance().last_update_time
        return response

    @app.route('/gen_update', methods=['POST'])
    def gen_update():
        task = ThreadTask(run=GlobalConfigs.instance().gen_and_request_update)
        ThreadPool.instance().get_thread().put_job(task)
        return {
            "status_code": 200,
            "message": "Server received your request!"
        }

    # Authenticate user
    @app.route('/login.html', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        # Declare the login form
        form = LoginForm(request.form)

        # Flask message injected into the page, in case of any errors
        msg = None

        # check if both http method is POST and form is valid on submit
        if form.validate_on_submit():

            # assign form data to variables
            username = request.form.get('username', '', type=str)
            password = request.form.get('password', '', type=str)

            if username == 'mgt':
                user = User(username, password)
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Unkkown user"

        return render_template('templates/layouts/default.html',
                               content=render_template('templates/pages/login.html', form=form, msg=msg))

    @app.route('/logout.html', methods=['GET', 'POST'])
    def logout():
        logout_user()
        return redirect(url_for('login'))

    socketio.run(app, host='0.0.0.0', port=GlobalConfigs.instance().get_port())


class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password


class LoginForm(FlaskForm):
    username = StringField(u'Username', validators=[DataRequired()])
    password = PasswordField(u'Password')
