# device_id: IMEI.
# - latitude.
# - longitude.
# - speed: km/h.
# - reliability: reliability of GPS (no use now, this number always 0).
# - satellite: number satellite.
# - type: (3 if it's mobile phone).
# - lock: 1 -> mobile screen is locked, 0 -> is unlocked.
# - datetime: YYYY-MM-DD HH:MM:SS (example: 2017-06-21 01:20:20).
# - option: another information.


class GPSData:
    def __init__(self, device_id, latitude, longitude, speed, reliability, satellite, type, lock, datetime, option):
        self.device_id = device_id
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.reliability = reliability
        self.satellite = satellite
        self.type = type
        self.lock = lock
        self.datetime = datetime
        self.option = option

    def toDict(self):
        return {
            "device_id": self.device_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "reliability": self.reliability,
            "satellite": self.satellite,
            "type": self.type,
            "lock": self.lock,
            "datetime": self.datetime,
            "option": self.option
        }
