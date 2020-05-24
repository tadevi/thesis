from queue import Queue

from modules.base import Map
from modules.network import Network
from modules.utils import log, get_configs
from server.channel import add_to_channel_analysis, add_to_channel_stream


class Main(Map):
    def __init__(self, configs):
        self.configs = configs
        self.queue = Queue(maxsize=3)

        node_config = get_configs('meta')
        network_module = Network({})
        d = {}
        if configs.get('analysis'):
            add_to_channel_analysis(configs['camera_id'], self.queue)
            d['camera_id'] = configs['camera_id']
            d['url'] = node_config['node_url'] + ":" + node_config['port'] + "/video?cam_id=" + configs['camera_id']
        else:
            add_to_channel_stream(configs['camera_id'], self.queue)
            d['stream_id'] = configs['camera_id']
            d['url'] = node_config['node_url'] + ":" + node_config['port'] + "/video?stream_id=" + configs['camera_id']

        network_module.post(configs['cloud_url'] + '/stream/', {
            **d,
            "name": configs['name'],
        })

    def run(self, inputs):
        super(Main, self).run(inputs)
        if self.queue.full():
            self.queue.get()
        self.queue.put(inputs)
