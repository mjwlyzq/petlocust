from libs.public import LocustPublic


class PKRankingClient(object):
    def __init__(self):
        super(PKRankingClient, self).__init__()
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.timeout = 5 * 60
        self.contentUniqueId = 49838
        self.businessId = 51510
        self.classroomType = "FOLLOWER_ASYNC_PK"

        self.trainingRecordIds = []
        self.roomId = None

    def send_post(self, client, userinfo):
        self.getCandidateList(client, userinfo)
        self.createRoom(client, userinfo)
        self.getScore(client, userinfo)

    def getCandidateList(self, client, userinfo):
        desc = '(PK候选者列表)'
        # virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = dict(classroomType=self.classroomType,
                       contentId=str(self.contentUniqueId),
                       businessId=str(self.businessId))
        url = f"{self.recordingHost}/taurus/follower-async-pk/candidate/list"
        resp = LocustPublic.post(client, url, taurus_headers, payload, desc)
        content = resp.get("content")
        self.trainingRecordIds = list(map(lambda c: c.get("trainingRecordId"), content))[:3]

    def createRoom(self, client, userinfo):
        desc = '(PK开房)'
        # virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = dict(classroomType=self.classroomType,
                       contentId=str(self.contentUniqueId),
                       model="MANUAL_ONE_TO_N",
                       trainingRecordIds=self.trainingRecordIds)
        url = f"{self.recordingHost}/taurus/classroom/multi/create-room"
        resp = LocustPublic.post(client, url, taurus_headers, payload, desc)
        content = resp.get("content")
        self.roomId = content.get("roomId")

    def getScore(self, client, userinfo):
        desc = '(获取PK分数)'
        virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        # taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = dict(roomId=self.roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        resp = LocustPublic.post(client, url, virgo_headers, payload, desc)
        content = resp.get("content")
        data = content.get("data")
