"""defines revision base class"""
from datetime import datetime
import requests
import mwparserfromhell as mwp

URL = "https://www.wikipedia.org/w/api.php"

class Revision():
    """revision object parses json revision info into consistent """

    def __init__(self, initjson: dict) -> None:
        self.json: dict = initjson
        self.init_to_none()
        for attr in [key for key in vars(self).keys() if key != "json"]:
            try:
                vars(self)[attr] = self.json[attr]
            except KeyError:
                pass # init JSON is missing this attr - nbd

    def init_to_none(self):
        """sets up class data members and initializes them to None """
        self.pageid: int = None
        self.title: str = None
        self.revid: int = None
        self.parentid: int = None
        self.minor: bool = None
        self.user: str = None
        self.userid: int = None
        self.timestamp: str = None
        self.size: int = None
        self.comment: str = None
        self.tags: list[str] = None

    def contains_tag(self, tag_list):
        """checks if a revision contains any tags from the parameter list of tags"""
        return all(item in self.tags for item in tag_list)

    def contains_keyword(self, keyword):
        """checks if a revision contains any keywords inside of the revision content"""
        content = self.get_diff()
        if content.find(keyword) > 0:
            return True
        return False

    def get_content(self):  # start and end time stamps???
        """ Returns the content of the page at this revision"""

        session = requests.Session()

        params = {
            "action": "parse",
            "format": "json",
            "oldid": self.revid,
            "prop": "text",
        }
        if self.revid is None:
            raise AttributeError("Revision ID missing")
        request = session.get(url=URL, params=params, timeout=5)
        data = request.json()["parse"]["text"]["*"]
        ret = mwp.parse(data)
        return str("".join(ret).replace("\n", ""))

    def get_diff(self, to_id: int = None):
        """ Returns the difference between this revision and its parent
        in this revision's article's history, unless a toId is specified in
        which case this revision is compared with toId.
        """
        if to_id is None:
            if self.parentid is None:
                raise AttributeError("Revision parent ID missing")
            to_id = self.parentid
        session = requests.Session()
        params = {
            # params for Compare API
            # https://www.mediawiki.org/wiki/API:Compare
            "action": "compare",
            "format": "json",
            "fromrev": self.revid,
            "torev": to_id
        }
        wp_response = session.get(url=URL, params=params).json()
        # Can we return something more user-friendly?
        # Automatically color ins and del tags?
        try:
            return str(mwp.parse(wp_response['compare']['*']))
        except (KeyError, ValueError):
            return self.get_content()

def timestamp_to_datetime(timestamp: str):
    """Converts the timestamp into a python-friendly datetime object
    for use in collections of revisions
    """
    if timestamp is None:
        raise AttributeError("Revision timestamp missing")
    year = int(timestamp[0:4])
    month = int(timestamp[4:6])
    day = int(timestamp[6:8])
    hour = int(timestamp[8:10])
    minute = int(timestamp[10:12])
    second = int(timestamp[12:14])
    ret = datetime(year, month, day, hour, minute, second)
    return ret
