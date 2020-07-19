from cv2 import cv2
from flask import *

from resource_manager.GlobalConfigs import GlobalConfigs
from rule_engine import RuleEngine
from server.channel import get_channel


def start_up():
    start_up_inputs = GlobalConfigs.instance().get_config('start_up')
    for input in start_up_inputs:
        rules = GlobalConfigs.instance().lookup_rules(input['name'])
        RuleEngine.instance().run(rules, input)


app = Flask(__name__)


@app.route('/')
def index():
    return "..."


'''
Receive stream from camera or lower layer fog node to process
json body request have format:
{
    "name": <rule name>,
    "camera_id":<camera id>,
    "type": "mjpeg" vs other
    "url" : <optional>, 
    ... additional fields
}
'''


@app.route('/stream/', methods=['POST'])
def stream():
    input = request.json
    rules = GlobalConfigs.instance().lookup_rules(input['name'])
    RuleEngine.instance().run(rules, input)
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
    json = request.json
    rule_name = json['name']
    input = json['data']

    rules = GlobalConfigs.instance().lookup_rules(rule_name)

    RuleEngine.instance().run(rules, input)
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
def fog_data():
    node_meta = GlobalConfigs.instance().get_config('meta')
    return node_meta


def make_web():
    start_up()
    app.run(host='0.0.0.0', port=GlobalConfigs.instance().get_port(), threaded=True)
