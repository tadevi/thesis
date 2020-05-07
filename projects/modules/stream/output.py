from importlib import import_module

import cv2
from flask import *

from modules.base import Filter, Map


def make_web(queue):
    app = Flask(__name__, template_folder='.')

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen():
        while True:
            frame = next(queue.get())
            _, frame = cv2.imencode('.JPEG', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    try:
        app.run(host='localhost', port=3000, threaded=True)
    except:
        print('unable to open port')


class CameraQueue:
    def __init__(self, configs):
        self.cam = cv2.VideoCapture(configs['url'])
        self.modules = list(map(self.__getModule__, configs['modules']))

    def __getModule__(self, module):
        configs = module['configs']
        call = import_module('.' + module['name'], module['package'])
        main = getattr(call, 'Main')
        return {
            'configs': configs,
            'call': call,
            'main': main(configs)
        }

    def get(self):
        while True:
            _, frame = self.cam.read()
            _continue = False
            for module in self.modules:
                if isinstance(module['main'], Filter):
                    if not module['main'].run(frame):
                        _continue = True
                        break
                elif isinstance(module['main'], Map):
                    frame = module['main'].run(frame)
                else:
                    break
            if not _continue:
                yield frame
            else:
                continue


queue = CameraQueue({
    'url': 0,
    'modules': [
        {
            'package': 'modules.image',
            'name': 'human_detection',
            'configs': {}
        }
    ]
})
make_web(queue)
