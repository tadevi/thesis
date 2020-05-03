from datetime import datetime

from modules.text.gps.storage import Main
from modules.text.gps.storage.GPSData import GPSData
from modules.text.gps.storage.StorageConfigs import StorageConfigs

gps_data = GPSData(
    device_id=0,
    latitude=45,
    longitude=160,
    speed=30,
    reliability=0,
    satellite=0,
    type=3,
    lock=0,
    datetime=datetime.now(),
    option=None
)

inputs = [gps_data.toDict()]
configs = StorageConfigs(
    collection_name="test"
)


# myclient = pymongo.MongoClient(configs.mongo_url)
# mydb = myclient[configs.db_name]
# mycol = mydb[configs.collection_name]
def run():
    Main(configs).run(inputs)
