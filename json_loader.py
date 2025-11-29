import json


class JsonLoader:
    def load(self, file_path) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)