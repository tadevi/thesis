from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    # return render_template('index.html')
    return 'index.html'


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def run():
    app.run(host='0.0.0.0', debug=True, threaded=True)


# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(Camera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    run()
