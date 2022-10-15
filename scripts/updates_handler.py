import os
import re

import utils

UPDATES_PATH: str = "./updates"

UPDATES_FILE_PATH: str = "./updates/listing.json"
RAW_GH_UPDATES_FORMAT: str = "https://raw.githubusercontent.com/virtual-puppet-project/.github/master/updates/{}"

DATE_GROUP: str = "date"
TITLE_GROUP: str = "title"
CONTENT_REGEX: str = r"(?P<date>([0-9]{4})-([0-1][0-9])-([0-2][0-9]))_(?P<title>\S+).txt"


class UpdateListings(dict):
    class Listing(list):
        def add_item(self, title: str, date: str, rel_path: str) -> None:
            self.append({
                "title": title,
                "date": date,
                "path": RAW_GH_UPDATES_FORMAT.format(rel_path)
            })

    def add_listing(self, listing_name: str) -> Listing:
        if listing_name in self:
            raise Exception("Listing {} already exists".format(listing_name))

        listing: self.Listing = self.Listing()

        self[listing_name] = listing

        return listing


def handle(repo_root: str) -> None:
    print("Processing updates")

    updates_dir: str = "{}/{}".format(repo_root, UPDATES_PATH)

    regex = re.compile(CONTENT_REGEX)
    update_listings: UpdateListings = UpdateListings()

    for item_name in os.listdir(updates_dir):
        content_dir: str = "{}/{}".format(updates_dir, item_name)
        if not os.path.isdir(content_dir):
            print("Invalid item found at {}".format(content_dir))
            continue

        listing: UpdateListings.Listing = update_listings.add_listing(
            item_name)
        for content_item in os.listdir(content_dir):
            rel_content_path: str = "{}/{}".format(item_name, content_item)

            regex_match = regex.search(content_item)
            if regex_match == None:
                print("Invalid file name at {}".format(rel_content_path))
                continue

            listing.add_item(regex_match.group(TITLE_GROUP),
                             regex_match.group(DATE_GROUP), rel_content_path)

    utils.write_json_file(UPDATES_FILE_PATH, update_listings)

    print("Finished processing updates")
