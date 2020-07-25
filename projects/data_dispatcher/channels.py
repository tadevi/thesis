from data_dispatcher.UrlToStream import UrlToStream
from data_dispatcher.subscribers import Subscriber
from modules import log
from resource_manager.GlobalConfigs import GlobalConfigs
from resource_manager.ThreadPool import ThreadPool
from resource_manager.ThreadTask import ThreadTask


class BaseChannel:
    # channel_id: name of flow, ex: traffic_camera, gps, ...
    def __init__(self, channel_id, data):
        self.channel_id = channel_id
        self.subscribers = {}
        self.__init_subscribers__(data)

    def __init_subscribers__(self, data):
        rules = GlobalConfigs.instance().config.get('rules').get(self.channel_id)
        index = 0
        for rule in rules:
            id = self.__get_subscriber_id__(self.channel_id, index)
            modules_meta = rule.get('modules')
            self.subscribe(Subscriber(id, data, modules_meta))
            index += 1

    def __get_subscriber_id__(self, channel_id, index):
        return channel_id + str(index)

    def subscribe(self, subscriber):
        self.subscribers[subscriber.id] = subscriber

    def unsubscribe(self, subscriber_id):
        self.subscribers[subscriber_id].on_unsubscribe()
        self.subscribers.pop(subscriber_id)

    def on_next(self, item):
        for subscriber_id, subscriber in self.subscribers.items():
            subscriber.on_next(item)


class StreamChannel(BaseChannel):
    def __init__(self, channel_id, data):
        super().__init__(channel_id, data)
        self.tag = "StreamChannel"

        # start a separate thread for reading input
        task = ThreadTask(run=self.__start_reading__, params=(data,))
        ThreadPool.instance().get_thread().put_job(task)

    def __start_reading__(self, data):
        log.v(self.tag, "__start_reading__")
        url_to_stream = UrlToStream(data)
        while True:
            item = url_to_stream.get()
            self.on_next(item)


class ScalaChannel(BaseChannel):
    def __init__(self, channel_id, data):
        super().__init__(channel_id, data)
