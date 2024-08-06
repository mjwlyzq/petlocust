from libs.public import LocustPublic


class MedalClient(object):
    def __init__(self):
        super(MedalClient, self).__init__()
        self.timeout = 5 * 60

    def send_post(self, client, userinfo):
        print(userinfo)
        desc = '(发勋章)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {
            "bizCode": "ACTIVITY_PLATFORM",
            "items": [{
                "accountId": userinfo.get("authentication").get("accountId"),
                "medalCode": "MEDAL_SHARE_JOY_202203"
            }]
        }

        url = 'http://stable-up-shura-nt.qa.fiture.com/user/medal/batch/dispatch-medal'
        LocustPublic.post(client, url, taurus_headers, payload, desc)
