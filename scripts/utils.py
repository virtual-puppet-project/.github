import json
import yaml
from typing import Dict, List, Union


def read_json_file(path: str) -> Dict:
    print("Starting read for {}".format(path))

    f = open(path, "r")

    data = json.load(f)

    f.close()

    if not isinstance(data, Dict):
        raise Exception("Unexpected json data, expected a Dictionary")

    print("Finished read for {}".format(path))

    return data


def write_json_file(path: str, data: Dict[str, Union[str, Dict[str, str]]]) -> None:
    print("Starting write for {}".format(path))

    f = open(path, "w")

    json.dump(data, f, indent=4)

    f.close()

    print("Finished write for {}".format(path))


def read_yaml_file(path: str) -> Dict:
    print("Starting read for {}".format(path))

    f = open(path, "r")

    data = yaml.safe_load(f)

    f.close()

    if not isinstance(data, Dict):
        raise Exception("Unexpected yaml data, expected a Dictionary")

    print("Finished read for {}".format(path))

    return data


def write_str_file(path: str, data: str) -> None:
    print("Starting write for {}".format(path))

    f = open(path, "w")

    f.write(data)

    f.close()

    print("Finished write for {}".format(path))
