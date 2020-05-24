import json
import time

config_name = './config/config.json'

configs = {

}


def current_milli_time():
    return int(round(time.time() * 1000))


def json_encode(document: dict):
    if document.get('_id') is not None:
        document['_id'] = str(document.get('_id'))
    return document


def get_configs(name=None):
    global configs
    if configs == {}:
        with open(config_name, 'r') as f:
            json_config = json.load(f)
            configs = {
                **configs,
                **json_config
            }
    if name is None:
        return configs
    return configs.get(name)


def get_node_ip():
    global configs
    if configs.get('node_ip') is None:
        import urllib.request
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        configs['node_ip'] = external_ip

    return configs.get('node_ip')


def lookup_rule(input):
    with open(config_name, 'r') as f:
        json_config = json.load(f)
        rules = json_config['rules']
        rules = list(filter(lambda x: x['name'] == input['name'], rules))
        if not len(rules) == 1:
            return "Rule for this type not found!"
        return {
            **rules[0],
            **input
        }
