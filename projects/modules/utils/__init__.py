import time


def current_milli_time():
    return int(round(time.time() * 1000))


def json_encode(document: dict):
    if document.get('_id') is not None:
        document['_id'] = str(document.get('_id'))
    return document
