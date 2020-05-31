from resource_manager.GlobalConfigs import GlobalConfigs

from server.http import make_web

GlobalConfigs.instance().set_config('fog2.json')

make_web()
