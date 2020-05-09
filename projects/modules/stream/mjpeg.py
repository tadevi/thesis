from threading import Thread

from cv2 import cv2
from flask import Flask, render_template, Response

from modules.base import Map


def make_web(generator):
    app = Flask(__name__, template_folder='.')

    @app.route('/')
    def index():
        return render_template('index.html')

    def gen():
        while True:
            frame = next(generator())
            _, frame = cv2.imencode('.JPEG', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tostring() + b'\r\n')

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('video?id=<id>')
    def video(id):
        return {
            "status":"success",
            "id": id
        }
    return app


class Main(Map):
    def __init__(self, configs):
        self.configs = configs
        self.input = None
        self.server = None

    def gen(self):
        while True:
            print("self.input in generator ", self.input)
            if not (self.input is None):
                yield self.input

    def make_server(self):
        if self.server is None:
            self.server = make_web(self.gen)
            self.server.run(host='localhost', port=3100, threaded=True)
        return self.server

    def run(self, inputs):
        super(Main, self).run(inputs)
        if self.server is None:
            Thread(target=self.make_server, args=()).start()
        self.input = inputs
