import time
import socket


def current_milli_time():
    return int(round(time.time() * 1000))


def json_encode(document: dict):
    if document.get('_id') is not None:
        document['_id'] = str(document.get('_id'))
    return document


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_base_url(ip, port):
    if ip is not None and port is not None:
        return "http://" + ip + ":" + port
    else:
        return None