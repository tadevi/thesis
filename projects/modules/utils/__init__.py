import json
import time

config_name = './config/config.json'


def current_milli_time():
    return int(round(time.time() * 1000))


def json_encode(document: dict):
    if document.get('_id') is not None:
        document['_id'] = str(document.get('_id'))
    return document


def get_configs(name):
    with open(config_name, 'r') as f:
        json_config = json.load(f)

        return json_config.get(name)
