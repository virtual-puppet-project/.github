import datetime
from typing import Dict, List

import utils

INPUT_DATA_FILE_PATH: str = "./data/data.yaml"

RAW_DATA_FILE_PATH: str = "./data/raw.json"
AVAILABLE_TRACKERS_FILE_PATH: str = "./data/available_trackers.json"
PROFILE_README_FILE_PATH: str = "./profile/README.md"

DATA_NOT_FOUND: str = "Data not found"


class Data(object):
    class Maintainer(object):
        username: str
        display_name: str
        github_url: str

    maintainers: Dict[str, Maintainer]

    class Linkable(object):
        name: str
        description: str
        repo_url: str
        download_url: str
        upstream_name: str
        upstream_url: str
        maintainer: str

    applications: Dict[str, Linkable]
    trackers: Dict[str, Linkable]
    libraries: Dict[str, Linkable]

    def __init__(self) -> None:
        self.maintainers = {}
        self.applications = {}
        self.trackers = {}
        self.libraries = {}

    def __str__(self) -> str:
        r: str = ""

        for container in vars(self).values():
            for val in container.values():
                for k, v in vars(val).items():
                    r += "{}: {}\n".format(k, v)

        return r

    def parse_maintainers(self, data: List[Dict[str, str]]) -> None:
        for d in data:
            m = self.Maintainer()

            m.username = d.get("username", DATA_NOT_FOUND)
            m.display_name = d.get("display_name", m.username)
            m.github_url = d.get("github_url", DATA_NOT_FOUND)

            self.maintainers[m.username] = m

    def parse_linkable(self, container: Dict[str, Linkable], data: List[Dict[str, str]]) -> None:
        for d in data:
            l = self.Linkable()

            l.name = d.get("name", DATA_NOT_FOUND)
            l.description = d.get("description", DATA_NOT_FOUND)
            l.repo_url = d.get("repo_url", DATA_NOT_FOUND)
            l.download_url = d.get("download_url", DATA_NOT_FOUND)
            l.upstream_name = d.get("upstream_name", l.name)
            l.upstream_url = d.get("upstream_url", l.repo_url)
            l.maintainer = d.get("maintainer", DATA_NOT_FOUND)

            l.description = l.description.replace("$NAME_UPSTREAM_URL",
                                                  "[{}]({})".format(l.upstream_name, l.upstream_url))
            if l.maintainer in self.maintainers:
                m: self.Maintainer = self.maintainers[l.maintainer]
                l.maintainer = "[{}]({}) ({})".format(
                    m.username, m.github_url, m.display_name)

            container[l.name] = l


def _generate_profile_readme(data: Data) -> str:
    r: str = ""

    r += """
<!--
THIS FILE IS AUTO-GENERATED. ALL CHANGES MADE HERE WILL BE LOST.
Last generated datetime (UTC): {}
-->
    """.format(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")).strip()

    def create_newline(times: int = 1) -> str:
        return "\n" * times

    def create_table_header() -> str:
        r = """
| Name | Description |
| --- | --- |
        """.strip()
        return "{}\n".format(r)

    def create_table_row(l: Data.Linkable) -> str:
        return "| [{}]({}) | {} |\n".format(l.name, l.repo_url, l.description)

    r += create_newline(2)

    r += "# Virtual Puppet Project"
    r += create_newline(2)

    r += "## Applications"
    r += create_newline(2)

    r += create_table_header()
    for app in data.applications.values():
        r += create_table_row(app)

    r += create_newline()

    r += "## Trackers"
    r += create_newline(2)

    r += create_table_header()
    for tracker in data.trackers.values():
        r += create_table_row(tracker)

    r += create_newline()

    r += "## Libraries"
    r += create_newline(2)

    r += create_table_header()
    for lib in data.libraries.values():
        r += create_table_row(lib)

    r += create_newline()

    r += "---"
    r += create_newline()

    return r


def handle(repo_root: str) -> None:
    print("Processing raw data")

    raw_data = utils.read_yaml_file(
        "{}/{}".format(repo_root, INPUT_DATA_FILE_PATH))

    for i in ["maintainers", "applications", "trackers", "libraries"]:
        if not i in raw_data:
            raise Exception(
                "No {} found, this is definitely an error".format(i))

    data = Data()

    data.parse_maintainers(raw_data["maintainers"])

    for a, b in [
            (data.applications, raw_data["applications"]),
            (data.trackers, raw_data["trackers"]),
            (data.libraries, raw_data["libraries"])]:
        data.parse_linkable(a, b)

    print("Processing trackers")

    available_trackers = {}
    for tracker_name, tracker_data in data.trackers.items():
        available_trackers[tracker_name] = tracker_data.download_url

    print("Writing raw file")

    utils.write_json_file(
        "{}/{}".format(repo_root, RAW_DATA_FILE_PATH), raw_data)

    print("Writing trackers file")

    utils.write_json_file(
        "{}/{}".format(repo_root, AVAILABLE_TRACKERS_FILE_PATH), available_trackers)

    print("Writing profile README")

    utils.write_str_file("{}/{}".format(repo_root,
                                        PROFILE_README_FILE_PATH), _generate_profile_readme(data))

    print("Finished processing raw data")
