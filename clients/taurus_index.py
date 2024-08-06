from libs.public import LocustPublic


class TaurusIndexClient(object):
    def __init__(self):
        super(TaurusIndexClient, self).__init__()
        self.timeout = 5 * 60

    def send_post(self, client, userinfo):
        self.prepare(client, userinfo)
        self.join()

    def prepare(self, client, userinfo):
        self.client = client
        self.userinfo = userinfo

    def index(self):
        desc = '(首页Index)'
        taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'], self.userinfo['authentication'])
        payload = {"types": [
            "COACH_DYNAMIC",
            "OFFICIAL_DYNAMIC",
            "COMMENT"
        ]
        }

        url = 'http://stable.up-aldebaran.nt.qa.fiture.com/index'
        LocustPublic.post(self.client, url, taurus_headers, payload, desc)

    def join(self):
        desc = '(加入组)'
        taurus_headers = LocustPublic.taurus_headers(self.userinfo['taurus_headers'], self.userinfo['authentication'])
        payload = dict(id="4")
        url = 'http://stable.up-aldebaran.nt.qa.fiture.com/group/join'
        LocustPublic.post(self.client, url, taurus_headers, payload, desc)
