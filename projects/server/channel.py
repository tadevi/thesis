from modules.utils import log

channel_analysis = {}
channel_stream = {}

'''
                           Fog 1                  Fog 2                         Cloud
    Camera ------>      start_up --------------> analysis -------------------> analysis

'''


def add_to_channel_analysis(channel_id, queue):
    channel_analysis[channel_id] = queue


def add_to_channel_stream(channel_id, queue):
    channel_stream[channel_id] = queue


def get_channel(name):
    if name == 'analysis':
        return channel_analysis
    else:
        return channel_stream


def clear_from_channel(id):
    channel_stream.pop(id, None)
    channel_analysis.pop(id, None)
