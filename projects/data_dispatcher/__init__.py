from data_dispatcher.channels import ScalaChannel, BaseChannel, StreamChannel
from resource_manager.Singleton import Singleton


class DataDispatcher(metaclass=Singleton):
    @staticmethod
    def instance():
        return DataDispatcher()

    def __init__(self):
        self.__channels__ = {}

    def dispatch(self, data):
        type_name = data['name']
        channel = self.__channels__.get(type_name)
        if channel is None:
            channel_id = type_name
            if data.get('type') == 'scala':
                channel = ScalaChannel(channel_id, data)
            else:
                channel = StreamChannel(channel_id, data)
            self.__channels__[channel_id] = channel

        if data.get('type') == 'scala':
            channel.on_next(data)
        # stream channel will get next item itself by reading from url
