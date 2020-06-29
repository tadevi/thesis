from resource_manager.GlobalConfigs import GlobalConfigs

global_configs = GlobalConfigs.instance()
global_configs.node_meta_name = "node_meta3.json"
global_configs.init_configs()

if global_configs.layer != 3:
    from server.http import make_web

    make_web()
else:
    from server.cloud_http import make_web

    make_web()
