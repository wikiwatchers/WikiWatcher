"""defines revision base class"""
from datetime import datetime
import requests
import mwparserfromhell as mwp
from bs4 import BeautifulSoup

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
    
    def add_color_coding_to_text(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        ins_tags = soup.find_all('ins')
        for ins in ins_tags:
            ins.attrs['style'] = 'background-color: green'
        del_tags = soup.find_all('del')
        for d in del_tags:
            d.attrs['style'] = 'background-color: red'
        #<ins> <del>
        return content

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
        color_coded_response = self.add_color_coding_to_text(wp_response['compare']['*'])
        # Can we return something more user-friendly?
        # Automatically color ins and del tags?
        try:
            return color_coded_response
            #return str(mwp.parse(color_coded_response))
        except (KeyError, ValueError):
            return self.get_content()
            

    def get_revision_key(self, attr):
        """gets the revision attribute, which is passed in as a string"""
        if attr == "":
            raise KeyError
        try:
            return vars(self)[attr]
        except KeyError:
            return None

#if __name__ == "__main__":
#    rev = Revision()