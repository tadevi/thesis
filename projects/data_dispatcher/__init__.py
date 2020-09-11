from data_dispatcher.channels import ScalaChannel, BaseChannel, StreamChannel
from resource_manager.Singleton import Singleton


class DataDispatcher(metaclass=Singleton):
    @staticmethod
    def instance():
        return DataDispatcher()

    def __init__(self):
        self.channels = {}

    def dispatch(self, data):
        channel_name = data['name']
        if data.get('type') == 'scala':
            channel_id = channel_name
        else:
            channel_id = channel_name + data['camera_id']

        channel = self.channels.get(channel_id)
        if channel is None:
            if data.get('type') == 'scala':
                channel = ScalaChannel(channel_name, channel_name, data)
            else:
                channel = StreamChannel(channel_id, channel_name, data)
            self.channels[channel_id] = channel

        if data.get('type') == 'scala':
            channel.on_next(data)
        # stream channel will get next item itself by reading from url

    def stream_channels_data(self):
        stream_channels = dict(filter(lambda elem: isinstance(elem[1], StreamChannel), self.channels.items()))
        return list(map(lambda channel: channel.stream_data, stream_channels.values()))
