import os
import queue
import random

from libs.public import LocustPublic
from libs.timeUtil import TimeUtil

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class GoddessClient(object):
    def __init__(self):
        super(GoddessClient, self).__init__()
        self.timeout = 5 * 60

    def live_start(self, client, userinfo):
        desc = '(直播开始)'
        LocustPublic.isGray = False
        taurus_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        payload = {"trainingType": "LIVING_MODE", "contentUniqueId": userinfo['contentUniqueId'],
                   "clientLocalTime": TimeUtil.now(),
                   "deviceMode": "DOMESTIC", "source": "TAURUS", "contentRelationship": {}}
        url = 'http://content.qa.fiture.com/virgo/training/report/live/start'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def statistics_get(self, client, userinfo, recordIdQueue: queue.Queue):
        desc = '(Virgo结果页)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        recordId = recordIdQueue.get()
        payload = dict(trainingRecordId=recordId)
        url = 'http://content.qa.fiture.com/virgo/training/statistics/get'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def send_reserve(self, client, userinfo):
        desc = '(直播课预约)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"id": userinfo['courseId']}
        url = 'http://content.qa.fiture.com/taurus/course/reserve'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def section_push(self, client, userinfo):
        desc = '(Virgo环环节据上报)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        with open(PATH('./../recordId.txt'), 'r', encoding='utf-8') as f:
            data = f.read().split('\n')
        payload = {"sectionName": "训练", "score": 0.0, "trainingRecordId": f"{random.choice(data)}",
                   "startTime": TimeUtil.now(),
                   "sectionId": "97859", "endTime": TimeUtil.now() + 600, "effectiveDuration": 57000}
        url = 'http://content.qa.fiture.com/virgo/training/course-section/push'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def live_end(self, client, userinfo, recordIdQueue: queue.Queue):
        desc = '(直播结束)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        pointsList = [
            [{"x": 0, "y": 0.0}, {"x": 1, "y": 0.0},
             {"x": 2, "y": 0.0}, {"x": 3, "y": 0.0},
             {"x": 4, "y": 0.0}, {"x": 5, "y": 0.0},
             {"x": 6, "y": 0.0}, {"x": 7, "y": 0.0},
             {"x": 8, "y": 0.0}, {"x": 9, "y": 0.0},
             {"x": 10, "y": 0.0}, {"x": 11, "y": 0.0},
             {"x": 12, "y": 0.0}],
            [], [], [], [], [], [], [], [], [],
        ]
        recordId = recordIdQueue.get()
        # with open(PATH('./../recordId.txt'), 'r', encoding='utf-8') as f:
        #     # data = f.read().split('\n')
        #     data = f.readlines()
        #     data = list(map(lambda line: line.strip().strip("\'\""), data))
        payload = {"duration": 13637, "effectiveness": "EFFECTIVE", "trainingRecordId": str(recordId),
                   "endType": "FINISH",
                   "playDuration": 0, "motionEquivalentChart": {"chartType": "MOTION_EQUIVALENT",
                                                                "points": random.choice(pointsList)},
                   "isAsyncPK": False,
                   "clientLocalTime": TimeUtil.now(), "calories": 0, "effectiveDuration": 0}
        url = 'http://content.qa.fiture.com/virgo/training/report/end'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def training_results_v3(self, client, userinfo, recordIdQueue: queue.Queue):
        desc = '(查询用户训练结果页V3)'
        recordId = recordIdQueue.get()
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])

        payload = {"trainingRecordId": recordId, "queryScene": "TRAINING_COMPLETE"}
        url = 'http://stable-cp-content-nt.qa.fiture.com/taurus/training/results/info/v3'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def h5_data(self, client, userinfo, recordIdQueue: queue.Queue):
        desc = '(查询h5模版数据)'
        recordId = recordIdQueue.get()
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])

        # payload = {"sourceType": "RICH_SHARE", "recordId": recordId, "contentId": userinfo['contentUniqueId'],
        #            "roomId": "1526835014231285762",
        #            "fieldKeys": ["totalRepeat", "multiTrainingAvatars", "courseEndTime", "avatarUrl", "achievement",
        #                          "level", "backgroundImage", "encouragingWords", "multiTraining", "calories",
        #                          "userName", "duration", "titleImage", "score", "courseName", "liveCourse", "qrCode",
        #                          "multiMovementCount", "rank", "totalGroup", "transcendental", "sourceImage",
        #                          "newRecord", "qrCodeImage"], "richShareModuleIds": [None, 151, 5]}

        payload = {"sourceType": "RICH_SHARE", "recordId": recordId, "contentId": userinfo['contentUniqueId'],
                   "roomId": "1526835014231285762",
                   "fieldKeys": ["totalRepeat", "multiTrainingAvatars", "courseEndTime", "avatarUrl", "achievement",
                                 "level", "backgroundImage", "encouragingWords", "multiTraining", "calories",
                                 "userName", "duration", "titleImage", "score", "courseName", "liveCourse",
                                 "multiMovementCount", "rank", "totalGroup", "transcendental", "sourceImage",
                                 "newRecord", "qrCodeImage"], "richShareModuleIds": [None, 151, 5]}
        url = 'http://stable-cp-content-nt.qa.fiture.com/taurus/training/popup/h5/data'
        LocustPublic.post(client, url, taurus_headers, payload, desc)


if __name__ == "__main__":
    GoddessClient().live_end(None, dict(virgo_headers=None, authentication=None))
