#!/usr/bin/env python

"""
Script for automatically updating the github profile readme and files under the
data/ directory.

Expects a file called raw.json at data/raw.json
"""

import os

import data_handler
import updates_handler


def main() -> None:
    repo_root: str = "{}/../".format(
        os.path.dirname(os.path.realpath(__file__)))

    print("Generating content")

    data_handler.handle(repo_root)
    updates_handler.handle(repo_root)

    print("Finished generating content")


if __name__ == "__main__":
    main()
