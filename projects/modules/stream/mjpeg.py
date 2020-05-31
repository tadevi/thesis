from queue import Queue

from modules.base import Map
from modules.network import Network
from modules.utils import log
from resource_manager.GlobalConfigs import GlobalConfigs
from server.channel import add_to_channel_analysis, add_to_channel_stream


class Main(Map):
    def broadcast_stream(self):
        if self.configs.get('type') == "analysis":
            add_to_channel_analysis(self.configs['camera_id'], self.queue)
        else:
            add_to_channel_stream(self.configs['camera_id'], self.queue)

    def push_to_cloud(self):
        network_module = Network({})
        d = {}

        node_url = GlobalConfigs.instance().get_node_ip()
        port = GlobalConfigs.instance().get_port()
        camera_id = self.configs['camera_id']
        if self.configs.get('type') == "stream":
            add_to_channel_stream(self.configs['camera_id'], self.queue)
            d['camera_id'] = self.configs['camera_id']
            d['url'] = 'http://' + node_url + ":" + str(port) + "/video?stream_id=" + camera_id

            network_module.post(self.configs['cloud_url'] + '/camera/', {
                **d,
                "name": self.configs['name'],
            })
        else:
            d['camera_id'] = self.configs['camera_id']
            d['url'] = 'http://' + node_url + ":" + str(port) + "/video?analysis_id=" + camera_id

            network_module.post(self.configs['cloud_url'] + '/stream/', {
                **d,
                "name": self.configs['name'],
            })

        log.i("View stream at", d['url'])

    def __init__(self, configs):
        self.configs = configs
        self.queue = Queue(maxsize=3)
        self.broadcast_stream()
        self.push = False

    def run(self, inputs):
        super(Main, self).run(inputs)
        if not self.push and not self.queue.empty():
            self.push_to_cloud()
            self.push = True

        if self.queue.full():
            self.queue.get()
        self.queue.put(inputs)

        return inputs
