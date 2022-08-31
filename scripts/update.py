#!/usr/bin/env python

"""
Script for automatically updating the github profile readme and files under the
data/ directory.

Expects a file called raw.json at data/raw.json
"""

from enum import Enum
import os
import json

RAW_DATA_FILE_PATH: str = "/data/raw.json"
AVAILABLE_TRACKERS_FILE_PATH: str = "/data/available_trackers.json"
PROFILE_README_FILE_PATH: str = "profile/README.md"

DATA_NOT_FOUND: str = "Data not found"


class Data(object):
    class Maintainer(object):
        username: str
        display_name: str
        github_url: str

    maintainers: dict[str, Maintainer]

    class Linkable(object):
        name: str
        description: str
        repo_url: str
        download_url: str
        upstream_name: str
        upstream_url: str
        maintainer: str

    applications: dict[str, Linkable]
    trackers: dict[str, Linkable]
    libraries: dict[str, Linkable]

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

    def parse_maintainers(self, data: list[dict[str, str]]) -> None:
        for d in data:
            m = self.Maintainer()

            m.username = d.get("username", DATA_NOT_FOUND)
            m.display_name = d.get("display_name", m.username)
            m.github_url = d.get("github_url", DATA_NOT_FOUND)

            self.maintainers[m.username] = m

    def parse_linkable(self, container: dict[str, Linkable], data: list[dict[str, str]]) -> None:
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
                l.maintainer = "[{}]({})".format(
                    m.display_name, m.github_url)

            container[l.name] = l


def _read_json_file(path: str) -> dict:
    print("Starting read for {}".format(path))

    f = open(path, "r")

    data = json.load(f)

    f.close()

    if not isinstance(data, dict):
        raise Exception("Unexpected json data, expected a Dictionary")

    print("Finished read for {}".format(path))

    return data


def _write_json_file(path: str, data: dict[str, str]) -> None:
    print("Starting write for {}".format(path))

    f = open(path, "w")

    json.dump(data, f, indent=4)

    f.close()

    print("Finished write for {}".format(path))


def _write_str_file(path: str, data: str) -> None:
    print("Starting write for {}".format(path))

    f = open(path, "w")

    f.write(data)

    f.close()

    print("Finished write for {}".format(path))


def _generate_profile_readme(data: Data) -> str:
    r: str = ""

    r += "# Virtual Puppet Project\n\n"

    r += "## Applications\n\n"

    def create_list_item(l: Data.Linkable) -> str:
        return "* [{}]({}) - {}\n".format(l.name, l.repo_url, l.description)

    for app in data.applications.values():
        r += create_list_item(app)

    r += "\n"

    r += "## Trackers\n\n"

    for tracker in data.trackers.values():
        r += create_list_item(tracker)

    r += "\n"

    r += "## Libraries\n\n"

    for lib in data.libraries.values():
        r += create_list_item(lib)

    return r


def main() -> None:
    repo_root: str = "{}/../".format(
        os.path.dirname(os.path.realpath(__file__)))

    print("Reading raw data")

    raw_data = _read_json_file(
        "{}/{}".format(repo_root, RAW_DATA_FILE_PATH))

    for i in ["maintainers", "applications", "trackers", "libraries"]:
        if i not in raw_data:
            raise Exception(
                "No {} found, this is definitely an error".format(i))

    data = Data()

    data.parse_maintainers(raw_data["maintainers"])

    data.parse_linkable(data.applications, raw_data["applications"])
    data.parse_linkable(data.trackers, raw_data["trackers"])
    data.parse_linkable(data.libraries, raw_data["libraries"])

    print("Processing trackers")

    available_trackers = {}
    for tracker_name, tracker_data in data.trackers.items():
        available_trackers[tracker_name] = tracker_data.download_url

    print("Writing trackers file")

    _write_json_file(
        "{}/{}".format(repo_root, AVAILABLE_TRACKERS_FILE_PATH), available_trackers)

    _write_str_file("{}/{}".format(repo_root,
                    PROFILE_README_FILE_PATH), _generate_profile_readme(data))

    print("Finished!")


if __name__ == "__main__":
    main()
