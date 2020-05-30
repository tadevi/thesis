
from resource_manager.GlobalConfigs import GlobalConfigs
from server.cloud_http import make_web

GlobalConfigs.instance().set_config('config.json')

make_web()
