import time

from libs.timeUtil import TimeUtil
from libs.public import LocustPublic
import itertools


class AiRealTimeRankClient(object):
    def __init__(self):
        super(AiRealTimeRankClient, self).__init__()
        self.contentHost = 'http://content.qa.fiture.com'
        self.timeout = 5 * 60
        self.contentUniqueId = 49838
        self.businessId = 51510
        self.classroomType = "TOPN_TIMELINE"

        self.contentInfo = {}
        self.movementList = []
        self.totalScore = 0

    def send_post(self, client, userinfo, nacos):
        if not (self.contentInfo and self.movementList):
            self.getCourseInfo(client, userinfo)
        self.getRealTimeRankData(client, userinfo)
        trainingRecordId = self.trainingStart(client, userinfo)
        while 1:
            try:
                if nacos.config.get("exit", False):
                    break
                time.sleep(1)
            except Exception as err:
                pass

        self.trainingEnd(client, userinfo, trainingRecordId)

    def getCourseInfo(self, client, userinfo):
        desc = '(课程详情)'
        virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        payload = dict(contentId=self.contentUniqueId)
        url = f'{self.contentHost}/virgo/content/detail'
        resp = LocustPublic.post(client, url, virgo_headers, payload, desc)
        content = resp.get("content")
        contentInfo = content.get("contentInfo")
        name = contentInfo.get("name")
        contentType = contentInfo.get("contentType")
        contenttype = contentInfo.get("type")
        period = contentInfo.get("period")
        duration = contentInfo.get("duration")
        status = contentInfo.get("status")
        sections = content.get("sections")
        subSections = list(itertools.chain.from_iterable(map(lambda section: section["subSections"], sections)))
        movementSubsections = list(
            filter(lambda section: "resourceType" in section and section["resourceType"] == "MOVEMENT",
                   subSections))
        movementList = list(
            map(lambda subsection: dict(movement=subsection["subSectionMovement"], start=subsection["start"],
                                        duration=subsection["duration"]), movementSubsections))

        assert status == "ONLINE", f"课程未上线: {status}"
        assert contentType == "COURSE", f"课程类型不支持: {contentType}"
        self.contentInfo = contentInfo
        self.movementList = movementList

    def trainingStart(self, client, userinfo):
        desc = '(课程开始)'
        virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        payload = dict(contentUniqueId=self.contentUniqueId,
                       trainingType="COURSE_MODE",
                       clientLocalTime=TimeUtil.now(),
                       deviceMode="DOMESTIC",
                       source="TAURUS",
                       contentRelationship={},
                       classroom=dict(type=self.classroomType)
                       )

        url = f'{self.contentHost}/virgo/training/report/start/v2'

        resp = LocustPublic.post(client, url, virgo_headers, payload, desc)
        trainingRecordId = resp.get("content").get("trainingRecordId")
        needReportScore = resp.get("content").get("reportDetail").get("needReportScore")
        assert needReportScore is True, "课程不支持上报AI评分!"
        return trainingRecordId

    def trainingEnd(self, client, userinfo, trainingRecordId: int):
        desc = '(课程结束)'
        virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        payload = dict(trainingRecordId=trainingRecordId,
                       effectiveness="EFFECTIVE",
                       endType="FINISH",
                       clientLocalTime=TimeUtil.now(),
                       calories=999,
                       duration=self.contentInfo.get("duration"),
                       playDuration=self.contentInfo.get("duration"),
                       effectiveDuration=self.contentInfo.get("duration"),
                       result=self.totalScore,
                       unit="SCORE"
                       )

        url = f'{self.contentHost}/virgo/training/report/end'
        LocustPublic.post(client, url, virgo_headers, payload, desc)

    def getRealTimeRankData(self, client, userinfo):
        desc = '(获取实时排行榜数据)'
        virgo_headers = LocustPublic.taurus_headers(userinfo['virgo_headers'], userinfo['authentication'])
        payload = dict(contentId=int(self.contentUniqueId),
                       businessId=str(self.businessId),
                       classroomType=self.classroomType,
                       accountId=userinfo.get('accountId'))
        url = f'http://stable-cp-recording-bff-nt.qa.fiture.com/recording/rank/ai-realtime/get/data'
        LocustPublic.post(client, url, virgo_headers, payload, desc)
