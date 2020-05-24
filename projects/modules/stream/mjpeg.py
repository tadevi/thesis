from queue import Queue

from modules.base import Map
from modules.network import Network
from modules.utils import log, get_configs, get_node_ip
from server.channel import add_to_channel_analysis, add_to_channel_stream


class Main(Map):
    def __init__(self, configs):
        self.configs = configs
        self.queue = Queue(maxsize=3)

        node_config = get_configs('meta')
        network_module = Network({})
        d = {}

        node_url = get_node_ip()
        port = node_config['port']
        camera_id = configs['camera_id']

        if configs.get('analysis'):
            add_to_channel_analysis(configs['camera_id'], self.queue)
            d['camera_id'] = configs['camera_id']
            d['url'] = node_url + ":" + str(port) + "/video?cam_id=" + camera_id
        else:
            add_to_channel_stream(configs['camera_id'], self.queue)
            d['stream_id'] = configs['camera_id']
            d['url'] = node_url + ":" + str(port) + "/video?stream_id=" + camera_id

        # network_module.post(configs['cloud_url'] + '/camera', {
        #     **d,
        #     "name": configs['name'],
        # })

    def run(self, inputs):
        super(Main, self).run(inputs)
        if self.queue.full():
            self.queue.get()
        self.queue.put(inputs)
