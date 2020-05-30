
from resource_manager.GlobalConfigs import GlobalConfigs
from server.http import make_web, start_up, app

GlobalConfigs.instance().set_config('config.json')

if __name__ == "__main__":
    start_up()
    app.run(port=GlobalConfigs.instance().get_port(), threaded=True)
