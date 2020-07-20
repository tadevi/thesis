import json

import requests

if __name__ == "__main__":
    with open("node_meta.json", 'r') as f:
        meta = json.load(f)

    cloud_gen_update_url = meta['cloud_url'] + "/gen_update"
    requests.post(cloud_gen_update_url, json={})
    print("POSTED to", cloud_gen_update_url)
