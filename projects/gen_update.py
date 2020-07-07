import json
import os
import time
import zipfile

from resource_manager.GlobalConfigs import GlobalConfigs


def gen_update():
    zip_modules()

    with open("node_meta3.json", 'r') as f:
        meta = json.load(f)
        meta["last_update_time"] = int(round(time.time() * 1000))

    with open('node_meta3.json', 'w') as f:
        json.dump(meta, f, indent=4)

    print("zipping modules done")


def zip_modules():
    project_root = GlobalConfigs.instance().project_root
    modules_path = os.path.join(project_root, "modules")

    zipf = zipfile.ZipFile('modules.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(modules_path):
        for file in files:
            zipf.write(os.path.join(os.path.relpath(root, GlobalConfigs.instance().project_root), file))
    zipf.close()


if __name__ == "__main__":
    gen_update()
