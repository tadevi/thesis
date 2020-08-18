import os

from resource_manager.GlobalConfigs import GlobalConfigs

global_configs = GlobalConfigs.instance()
global_configs.node_meta_name = "node_meta.json"
global_configs.project_root = os.path.dirname(os.path.abspath(__file__))
global_configs.init_node()

if global_configs.is_cloud:
    from server.cloud_http import make_web

    make_web()
else:
    from server.http import make_web

    make_web()
