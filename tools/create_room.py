import json
import random
from time import sleep

import requests

from libs.logger import log
from libs.myRedis import push_locust, rm_locust
from libs.nacos import NACOS
from libs.timeUtil import TimeUtil
nacos = NACOS("http://nacos.qa.fiture.com/nacos/v1/cs/configs?dataId=locust&group=DEFAULT_GROUP")


class Enm:
    UserInfo = 'UserInfo'


class CreateRoom:
    def __init__(self):
        self.RoomName = '一起练性能测试'
        self.createRoomCount = 1
        self.enterUserCount = 400
        self.bonePointCount = 400  # 有几个用户上报骨骼点
        self.contentUniqueIdList = [76402]
        self.classroomCode = 'MULTIPLAYER'
        self.recordingHost = 'http://stable-cp-recording-bff-nt.qa.fiture.com'
        self.userList = []
        self.userSet = []
        self.userGroupList = []
        self.roomIdList = []

    def create_room(self, headers):
        """
        Taurus创建约练房间
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = dict(contentIds=self.contentUniqueIdList,
                       subject=dict(type="aim", name="瘦肚子", value="stomach"),
                       classroomCode=self.classroomCode,
                       name=f"{self.RoomName}-{random.randint(1, 9999)}",
                       type="PUBLIC"
                       )
        url = f"{self.recordingHost}/taurus/classroom/multi/create-room"
        log.info(f"create-room: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        if resp['status'] != 'SUCCESS':
            raise Exception(resp)
        content = resp.get("content")
        roomId = content.get("roomId")
        log.info(f"创建约练房间: msg={payload}, resp={resp}")
        return roomId

    def join_room(self, roomId, headers):
        """
        Taurus加入约练房间
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = dict(roomId=roomId, deviceType="TAURUS")
        url = f"{self.recordingHost}/taurus/classroom/multi/user/join-room"
        log.info(f"join-room: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        if resp['status'] != 'SUCCESS':
            raise Exception(resp)
        content = resp.get("content")
        log.info(f"Taurus加入约练房间: msg={payload}, resp={resp}")

    def enter_room(self, roomId, headers):
        """
        Taurus进入约练房间
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = dict(
            source="TAURUS",
            clientLocalTime=TimeUtil.now(),
            classroom=dict(
                roomId=roomId,
                code=self.classroomCode,
            ),
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            trainingType="COURSE_MODE"
        )
        url = f"{self.recordingHost}/virgo/classroom/multi/user/enter"
        log.info(f"join-room: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        if resp['status'] != 'SUCCESS':
            raise Exception(resp)
        content = resp.get("content")
        log.info(f"Taurus进入约练房间: msg={payload}, resp={resp}")

    def join(self):
        from libs.public import TAAS
        from libs.public import LocustPublic
        taas = TAAS()
        for i in range(self.createRoomCount):
            user = taas.get_user()
            log.info(f'user：{json.dumps(user)}')
            virgo_headers = user.get('virgo_headers')
            taurus_headers = user.get('taurus_headers')
            authentication = user.get('authentication')
            taurus_headers = LocustPublic.taurus_headers(taurus_headers, authentication)
            virgo_headers = LocustPublic.taurus_headers(virgo_headers, authentication)
            roomId = self.create_room(taurus_headers)
            self.join_room(roomId, taurus_headers)
            self.enter_room(roomId, virgo_headers)
            self.userList.append(user)
            itemId, contentId, currentServerTime = self.get_resource(virgo_headers, roomId)
            self.userSet.append(dict(
                itemId=itemId,
                contentId=contentId,
                currentServerTime=currentServerTime,
                roomId=roomId,
                virgo_headers=virgo_headers,
                taurus_headers=taurus_headers,
            ))
            self.roomIdList.append(roomId)

    def user_grouping(self):
        from libs.public import TAAS
        for i in self.roomIdList:
            count = 0
            _bonePointCount = 0  # 骨骼点计数
            while True:
                user = TAAS().get_user()
                if not user:
                    raise Exception('没有user可用了')
                with open('accountId.txt', 'a', encoding='utf-8') as f:
                    f.write(user.get('accountId'))
                    f.write('\n')
                self.userGroupList.append(
                    dict(
                        roomId=i,
                        bonePoint=True if _bonePointCount < self.bonePointCount else False,
                        **user
                    )
                )
                count += 1
                _bonePointCount += 1
                if count >= self.enterUserCount:
                    break

    def set_user_to_redis(self):
        for i in self.userGroupList:
            push_locust(Enm.UserInfo, i)

    def clear(self):
        from tools.taas_tool import TAAS
        rm_locust(Enm.UserInfo)
        TAAS().end_room_end(self.RoomName)

    def init(self):
        from tools.taas_tool import TAAS
        TAAS().createSessionsQueue()

    def start(self):
        while True:
            isRun = nacos.config.get("together", {}).get("isRun", False)
            if isRun:
                try:
                    i = self.userSet.pop()
                except Exception:
                    i = None
                if i is None:
                    log.info(f'所有房间举手完成')
                    break
                self.start_room(i['virgo_headers'], i['contentId'], i['itemId'], i['roomId'])
                log.info(f'执行：{i}')
            else:
                sleep(2)
                log.info(f'等待开始执行start。。。')

    def get_resource(self, headers, roomId):
        """
        获取资源
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = dict(roomId=roomId)
        url = f"{self.recordingHost}/virgo/classroom/resource/get"
        log.info(f"join-room: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        if resp['status'] != 'SUCCESS':
            raise Exception(resp)
        content = resp.get("content")
        itemList = content.get('itemList')
        itemId = itemList[0].get('id')
        contentId = itemList[0].get('contentId')
        currentServerTime = itemList[0].get('currentServerTime')
        try:
            expectEndTime = itemList[0].get('expectEndTime')
        except Exception:
            expectEndTime = int(currentServerTime) + itemList[0].get('duration')
        log.info(f"获取资源: msg={payload}, resp={resp}")
        return itemId, contentId, expectEndTime

    def start_room(self, headers, contentId, itemId, roomId):
        """
        开始上课
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = dict(
            clientLocalTime=1679608800,
            contentUniqueId=contentId,
            deviceMode="DOMESTIC",
            deviceType="VIRGO",
            roomId=roomId,
            roomItemId=itemId,
            source="TAURUS",
            trainingType="COURSE_MODE"
        )
        url = f"{self.recordingHost}/virgo/classroom/user/start"
        log.info(f"join-room: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        if resp['status'] != 'SUCCESS':
            raise Exception(resp)
        content = resp.get("content")
        log.info(f"开始上课: msg={payload}, resp={resp}")


if __name__ == '__main__':
    obj = CreateRoom()
    obj.clear()
    obj.init()
    obj.join()
    obj.user_grouping()
    obj.set_user_to_redis()
    obj.start()