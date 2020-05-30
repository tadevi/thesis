from resource_manager.GlobalConfigs import GlobalConfigs

GlobalConfigs.instance().set_config('config.json')

if GlobalConfigs.instance().get_config('name') == 'cloud':
    from server.cloud_http import make_web

    make_web()
else:
    from server.cloud_http import make_web

    make_web()
