import json
import os
from pathlib import Path

from bson import ObjectId
from cv2 import cv2
from flask import Flask, render_template, request, Response, send_from_directory

from data_dispatcher import DataDispatcher
from modules import utils, storage
from resource_manager.GlobalConfigs import GlobalConfigs
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask
from server.channel import get_channel

tag = 'CLOUD HTTP'


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return o


encoder = JSONEncoder()


def get_database():
    return storage.Main(GlobalConfigs.instance().get_config('database'))


def make_web():
    app = Flask(__name__, template_folder='.')
    database = get_database()

    @app.route('/')
    def index():
        return render_template('index.html')

    '''
    ai services
    '''

    @app.route('/appearance', methods=['GET'])
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

    @app.route('/appearance', methods=['POST'])
    def save_appearance():
        json = request.json
        database.insert_one('appearance', json)
        return {
            "status": "success"
        }

    '''
    camera services
    '''

    @app.route('/camera', methods=['GET'])
    def get_camera():
        camera_id = request.args.get('id')

        if camera_id is not None:
            data = database.find_one('camera', {'camera_id': str(camera_id)})
            data = utils.json_encode(data) if data is not None else {}
        else:
            cursor = database.find_many('camera', {})
            data = [utils.json_encode(document) for document in cursor]

        return {"data": data}

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

    @app.route('/video')
    def video():
        if request.args.get('analysis_id') is not None:
            return Response(gen(get_channel('analysis'), request.args.get('analysis_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')
        elif request.args.get('stream_id') is not None:
            return Response(gen(get_channel('stream'), request.args.get('stream_id')),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/camera/', methods=['POST'])
    def add_camera():
        json = request.json
        database.insert_one('camera', json)
        return {
            "status": "success"
        }

    '''
    iot services
    '''

    @app.route('/traffic', methods=['GET'])
    def get_predict_traffic():
        pass

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
        modules_zip_path = os.path.join(project_root, "modules.zip")
        modules_zip_file = Path(modules_zip_path)
        if not modules_zip_file.is_file():
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

    app.run(host='0.0.0.0', port=GlobalConfigs.instance().get_port(), threaded=True)
