import argparse
import base64
import datetime
import hashlib
import os
import sqlite3

import pandas as pd
import requests


class Energy:
    def __init__(self, weeks: int = 10) -> None:
        self.headers = {
            'Authorization': f'Bearer {self.authenticate()}',
        }
        self.con = sqlite3.connect("data/energy.db")

        self.date_range = []

        for i in range(weeks):
            date = (datetime.date.today() - datetime.timedelta(weeks=i)).isocalendar()
            self.date_range.append(
                dict(year=date[0], week=date[1])
            )

    @staticmethod
    def authenticate():
        hashed = base64.b64encode(
            f"{os.environ['ENERGY_EMAIL']}:{hashlib.sha1(os.environ['ENERGY_PASSWORD'].encode('utf-8')).hexdigest()}"
            .encode("utf-8")
        ).decode()

        headers = {
            'Host': 'api.homewizardeasyonline.com',
            'Authorization': f'Basic {hashed}',
            'User-Agent': 'nl.homewizard.android.energy/1.10.1(46) Dalvik/2.1.0',
        }

        params = {'include': 'account'}

        response = requests.get('https://api.homewizardeasyonline.com/v1/auth/account/token', params=params,
                                headers=headers, verify=True)
        return response.json()["access_token"]

    def get_locations(self):
        response = requests.get('https://homes.api.homewizard.com/locations', headers=self.headers, verify=True)
        locations = [i["id"] for i in response.json()]
        return locations

    def get_devices(self, location: int):
        json_data = {
            'operationName': 'HomeScreen',
            'variables': {
                'homeId': location,
            },
            'query': 'query HomeScreen($homeId: Int!) { home(id: $homeId) { id currency hasEnergyPlus '
                     'navigationStartDate graphs { __typename ...Graph isEnabled source { supportsLiveData } '
                     'usedDevices { identifier } } devices { __typename ...CloudDeviceType } } }  fragment '
                     'GraphIdentifier on Graph { identifier }  fragment Graph on Graph { __typename ...GraphIdentifier '
                     'name type }  fragment CloudDeviceType on CloudDevice { type }',
        }

        response = requests.post('https://api.homewizard.energy/', headers=self.headers, json=json_data, verify=True)

        devices = list(set([i["usedDevices"][0]["identifier"] for i in response.json()["data"]["home"]["graphs"]]))

        parsed_devices = []
        for i in devices:
            if i.startswith("p1dongle"):
                parsed_devices.append({"devices": [i], "type": "main_connection", "values": True, "wattage": False,
                                       "fill": None, "three_phases": False})
                parsed_devices.append({"devices": [i], "type": "gas", "values": True, "wattage": False, "fill": None,
                                       "three_phases": False})
            elif i.startswith("watermeter"):
                parsed_devices.append({'devices': [i], 'type': 'water', 'values': True, 'wattage': False, 'fill': None,
                                       'three_phases': False})
        return parsed_devices

    def get_weekly_data(self, name: str, json_data: dict, year: int, week: int):
        response = requests.post(f'https://tsdb-reader.homewizard.com/devices/date/{year}/week/{week}',
                                 headers=self.headers, json=json_data, verify=True)
        df = pd.DataFrame(response.json()["values"])

        for i in range(len(df)):
            try:
                df.iloc[i:i + 1].to_sql(con=self.con, name=name, if_exists="append", index=False)
            except sqlite3.IntegrityError:
                pass  # or any other action

    def run(self):
        locations = self.get_locations()

        for location in locations:
            devices = self.get_devices(location=location)
            for i in devices:
                for date in self.date_range:
                    self.get_weekly_data(name=i["type"], json_data=i, year=date["year"], week=date["week"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", dest="weeks", help="Number of weeks to parse, default is 1", type=int)
    args = parser.parse_args()
    e = Energy(**vars(args))
    e.run()
