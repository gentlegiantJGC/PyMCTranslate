import json
import gzip


def load_json_gz(file_path: str):
    with gzip.open(file_path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'))
