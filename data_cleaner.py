import os
from tqdm import *


class DataCleaner():

    def __init__(self):
        self.protocol_clear_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "protocol.clr"
        )

    def clear_data(self, data_map):
        protocols = []
        with open(self.protocol_clear_file, "r") as f:
            for line in f.readlines():
                protocols.append(line.strip())

        new_data_map = {cls: [] for cls in data_map.keys()}
        for cls, d_list in tqdm(data_map.items()):
            new_d_list = []
            for data in d_list:
                if data["application_name"] in protocols:
                    continue
                new_d_list.append(data)
            new_data_map[cls] = new_d_list
        return new_data_map
