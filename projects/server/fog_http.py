import os

import pymongo
from cv2 import cv2
from flask import *
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_socketio import SocketIO

from data_dispatcher import DataDispatcher
from fake_data.fake_air import AirDataFaker
from modules import log, storage, utils, network
from resource_manager.GlobalConfigs import GlobalConfigs
from server.channel import get_channel
from server.cloud_http import User, LoginForm

tag = "Fog Http"


def start_up():
    start_ups = GlobalConfigs.instance().get_config('start_up')
    for data in start_ups:
        if data.get('camera_id') is not None and GlobalConfigs.instance().layer == 1:
            data['camera_id'] = str(GlobalConfigs.instance().position)
        DataDispatcher.instance().dispatch(data)


socketio = None


def get_database():
    return storage.Main(GlobalConfigs.instance().get_config('database'))


def make_web():
    start_up()
    app = Flask(__name__, template_folder='.')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    database = get_database()
    lm = LoginManager()  # flask-loginmanager
    lm.init_app(app)  # init the login manager
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # provide login manager with load_user callback
    @lm.user_loader
    def load_user(user_id):
        return User('mgt', '12345678')

    # App main route + generic routing
    @app.route('/', defaults={'path': 'notifications_fog.html'})
    @app.route('/<path>')
    def index(path):
        if not current_user.is_authenticated:
            # test
            user = User("mgt", "12345678")
            login_user(user)

            # return redirect(url_for('login'))

        try:

            # try to match the pages defined in -> pages/<input file>
            return render_template('templates/layouts/default_fog.html',
                                   content=render_template('templates/pages/' + path))
        except:

            return render_template('templates/layouts/default_fog.html',
                                   content=render_template('templates/pages/notifications_fog.html'))

    @app.route('/stream/', methods=['POST'])
    def stream():
        data = request.json
        DataDispatcher.instance().dispatch(data)
        on_new_camera_stream(data)
        return {
            "status_code": 200,
            "message": "Server received your request!"
        }

    def on_new_camera_stream(data):
        event_name = "new camera"
        channel_id = data['name'] + data['camera_id']
        event_args = DataDispatcher.instance().channels[channel_id].stream_data
        log.v(tag, "Emitted topic:", event_name, "with data:", event_args)

        socketio.emit(event_name, event_args)

        noti = {
            'timestamp': utils.current_milli_time(),
            'type': 'info',
            'message': 'At {}, camera with ID <b>{}</b> has connected to system'.format(
                utils.get_time_formatted(utils.current_milli_time()),
                data['camera_id']
            )
        }
        database.insert_one('notification', utils.json_encode(noti))
        socketio.emit("notification/Thu Duc", utils.json_encode(noti))

    @app.route('/iot/', methods=['POST'])
    def post_iot():
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

        if data['name'] == 'air' and event_args['pm25'] >= 100:
            if event_args['pm25'] < 150:
                type = 'warning'
                eval = "Unhealthy"
            elif event_args['pm25'] < 200:
                type = 'warning'
                eval = "Harmful"
            elif event_args['pm25'] < 300:
                type = 'primary'
                eval = "Very harmful"
            else:
                type = 'danger'
                eval = "Dangerous"

            noti = {
                'timestamp': utils.current_milli_time(),
                'type': type,
                'message': 'At {}, recorded PM2.5 value in {} is {}, which is evaluated as <b>{}</b>'.format(
                    utils.get_time_formatted(event_args['timestamp']),
                    event_args['location'],
                    event_args['pm25'],
                    eval
                )
            }
            database.insert_one('notification', utils.json_encode(noti))
            socketio.emit("notification/" + event_args['district'], utils.json_encode(noti))

        network.Network.instance().post(GlobalConfigs.instance().cloud_url + '/iot/', utils.json_encode(data))

    @app.route('/notifications', methods=['GET'])
    def get_notifications():
        cursor = database.db['notification'].find({}).sort("timestamp", pymongo.DESCENDING).limit(20)
        res = []
        for record in cursor:
            res.append(utils.json_encode(record))
        return {
            'data': res
        }

    def gen(channel, channel_id):
        queue = channel.get(channel_id)
        if queue is not None:
            last_frame = None
            while True:
                frame = queue.get()
                if frame is None:
                    frame = last_frame
                else:
                    _, frame = cv2.imencode('.JPEG', frame)
                    last_frame = frame

                yield (b'--frame\r\n'
                       b'Content-Type:image/jpeg\r\n'
                       b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
                                                                        b'\r\n' + frame.tostring() + b'\r\n')
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

    @app.route('/cameras', methods=['GET'])
    def camera_list():
        cameras = DataDispatcher.instance().stream_channels_data()
        return {"data": cameras}

    @app.route('/devices', methods=['GET'])
    def device_list():
        return {"data": [
            {
                'device_id': 'cam-1',
                'type': 'Camera',
                'location': 'Thu Duc (long=10.814412, lat=106.707704)',
                'post_url': 'http://{}:{}/stream/'.format(GlobalConfigs.instance().get_node_ip(),
                                                          GlobalConfigs.instance().get_port()),
                'post_data': {
                    "name": "traffic_camera",
                    "url": "https://youtu.be/bqNBUtPE8Ug",
                    "camera_id": "1",
                    "demo": "true",
                    "location": "Thu Duc (long=10.814412, lat=106.707704)",
                    "line_start": [0, 0.4],
                    "line_end": [1, 0.49]
                }
            },
            {
                'device_id': 'cam-2',
                'type': 'Camera',
                'location': 'Thu Duc (long=10.603849, lat=105.818374)',
                'post_url': 'http://{}:{}/stream/'.format(GlobalConfigs.instance().get_node_ip(),
                                                          GlobalConfigs.instance().get_port()),
                'post_data': {
                    "name": "traffic_camera",
                    "url": "https://youtu.be/nqjbLZrfVAU",
                    "camera_id": "2",
                    "demo": "true",
                    "location": 'Thu Duc (long=10.603849, lat=105.818374)',
                    "line_start": [0, 0.49],
                    "line_end": [1, 0.6]
                }
            },
            {
                'device_id': '',
                'type': 'Air Sensors',
                'location': 'Thu Duc',
                'post_url': 'http://{}:{}/fake_air'.format(GlobalConfigs.instance().get_node_ip(),
                                                           GlobalConfigs.instance().get_port()),
                'post_data': {
                    'district': 'Thu Duc'
                }
            },
            {
                'device_id': '',
                'type': 'Air Sensors',
                'location': 'District 10',
                'post_url': 'http://{}:{}/fake_air'.format(GlobalConfigs.instance().get_node_ip(),
                                                           GlobalConfigs.instance().get_port()),
                'post_data': {
                    'district': 'District 10'
                }
            }
        ]}

    @app.route('/fake_air', methods=['POST'])
    def start_faking_air_data():
        district = request.json.get('district')
        remote_url = "http://localhost:3000"
        fake_air = AirDataFaker(district, remote_url)

        fake_air.start_posting_fake_data()

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

    @socketio.on('my event')
    def handle_my_custom_event(json):
        log.v(tag, 'received json:', json)

    socketio.run(app, host='0.0.0.0', port=GlobalConfigs.instance().get_port())
