from time import sleep

from data_dispatcher.UrlToStream import UrlToStream
from data_dispatcher.subscribers import Subscriber
from modules import log, utils
from resource_manager.GlobalConfigs import GlobalConfigs
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask


class BaseChannel:
    # channel_name: name of flow, ex: traffic_camera, gps, ...
    # channel_id: channel_name if scala, else channel_name + camera_id
    def __init__(self, channel_id, channel_name, data):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.subscribers = {}
        self.__init_subscribers__(data)

    def __init_subscribers__(self, data):
        rules = GlobalConfigs.instance().config.get('rules').get(self.channel_name)
        index = 0
        for rule in rules:
            id = self.__get_subscriber_id__(self.channel_name, index)
            modules_meta = rule.get('modules')
            self.subscribe(Subscriber(id, data, modules_meta))
            index += 1

    def __get_subscriber_id__(self, channel_name, index):
        return channel_name + str(index)

    def subscribe(self, subscriber):
        self.subscribers[subscriber.id] = subscriber

    def unsubscribe(self, subscriber_id):
        self.subscribers[subscriber_id].on_unsubscribe()
        self.subscribers.pop(subscriber_id)

    def on_next(self, item):
        for subscriber_id, subscriber in self.subscribers.items():
            subscriber.on_next(item)


class StreamChannel(BaseChannel):
    def __init__(self, channel_id, channel_name, data):
        super().__init__(channel_id, channel_name, data)
        self.tag = "StreamChannel"
        self.stream_data = {
            'name': channel_name,
            'camera_id': data['camera_id'],
            'url': "http://{ip}:{port}/video?stream_id={cam_id}".format(ip=GlobalConfigs.instance().get_node_ip(),
                                                                        port=GlobalConfigs.instance().port,
                                                                        cam_id=data['camera_id'])
        }

        # start a separate thread for reading input
        task = ThreadTask(run=self.__start_reading__, params=(data,))
        ThreadPool.instance().get_thread().put_job(task)

    def __start_reading__(self, data):
        log.v(self.tag, "__start_reading__")
        url_to_stream = UrlToStream(data)
        last_time = utils.current_milli_time()
        while True:
            item = url_to_stream.get()
            self.on_next(item)
            cur_time = utils.current_milli_time()
            delay = max(0, 1 / url_to_stream.fps - (cur_time - last_time) / 1000)
            last_time = cur_time
            if delay > 0:
                sleep(delay)


class ScalaChannel(BaseChannel):
    def __init__(self, channel_id, channel_name, data):
        super().__init__(channel_id, channel_name, data)
