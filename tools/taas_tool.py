#!/usr/bin/env python
import json
import time
import requests
import logging

from libs.logger import log
from libs.timeUtil import TimeUtil


class Logger(object):
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    error_count = 0

    @classmethod
    def info(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.info(message)

    @classmethod
    def error(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.error(message)
        cls.error_count += 1

    @classmethod
    def debug(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.debug(message)

    @classmethod
    def warning(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.warning(message)

    @classmethod
    def set_debug_level(cls):
        cls.logger.setLevel(logging.DEBUG)

    @classmethod
    def set_info_level(cls):
        cls.logger.setLevel(logging.INFO)


def singleton(cls, *args, **kwargs):
    instances = dict()

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class BackendLogin(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.username = "chenjian"
        self.password = "P@ssw0rd!"
        self._token = ""

    def getToken(self):
        if not self._token:
            self._token = self._login()
        return self._token

    def _login(self):
        url = "http://keycloak.dev.fiture.com/auth/realms/fiture/protocol/openid-connect/token"
        payload = dict(username=self.username, password=self.password, client_id="cms", grant_type="password")
        s = requests.session()
        r = s.post(url=url, data=payload, verify=False, timeout=5)
        resp = r.json()
        access_token = resp['access_token']
        return f'Bearer {access_token}'


def getBackendSession():
    session = requests.session()
    session.headers.update(dict(Authorization=BackendLogin().getToken()))
    return session


@singleton
class TAAS(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.session = getBackendSession()

    def partflush(self):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        # url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        url = "http://localhost:8086/taas/enable-user/flush"
        payload = dict(accountIds=["1499293952350687233"])
        start = time.time()
        self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")

    def getSessions(self, accountCount=1, ignoreExpire=True):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        payload = dict(accountCount=accountCount, ignoreExpire=ignoreExpire)
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def createSessionsQueue(self):
        # url = "http://localhost:8086/taas/enable-user/list/v3"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v3"
        payload = dict(name="locust", maxLimit=2000)
        start = time.time()
        resp = self._push(url, payload)
        return resp.get("data")

    def getUsers(self):
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list"
        payload = dict()
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def forceUpdate(self):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        payload = dict(accountCount=1, ignoreExpire=True, forceUpdate=True)
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def checkSessions(self, ignoreExpire=False):
        sessions = self.getSessions(accountCount=100000, ignoreExpire=ignoreExpire)
        Logger.info(f"return : {len(sessions)} sessions")
        count = 0
        for s in sessions:
            Logger.info(
                f"phone: {s.get('phone')} taurus: {'OK' if 'taurus' in s else 'NOK'}, virgo: {'OK' if 'virgo' in s else 'NOK'}, expire: {s.get('expire')}")
            if not s:
                Logger.warning("empty seesion")
            elif "taurus" in s and "virgo" in s:
                count += 1
            elif "taurus" in s:
                Logger.warning(f"virgo session error: {s}")
            elif "virgo" in s:
                Logger.warning(f"taurus session error: {s}")
            else:
                Logger.warning(f"unkonw error: {s}")
        Logger.info(f"checked successful, available session: {count}")

    def _push(self, url, payload):
        Logger.debug(f"Request: POST {url}")
        Logger.debug(f"Request-body :{payload}")
        r = self.session.post(url, json=payload)
        Logger.debug(f"requests-headers: {r.request.headers}")
        Logger.debug(f"requests-body: {r.request.body}")
        try:
            resp = r.json()
        except Exception as err:
            Logger.error(f"error: {err}")
            Logger.error(r.text)
        return resp

    def search_room(self, headers, roomName):
        """
        查询所有课程
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = {
            "createStartTime": 1660579200000,
            "createEndTime": TimeUtil.now(),
            "pageNumber": 1,
            "pageSize": 60,
            "roomName": roomName
        }
        url = "http://stable-fe-pos-nt.qa.fiture.com/bff-api/cp-cms.nt/api/room/page"
        log.info(f"查询条件: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        log.info(resp)
        content = resp.get("content")
        records = content.get("records")
        roomIds = [i['roomId'] for i in records]
        log.debug(f"所有roomIds:, {roomIds}")
        return roomIds

    def end_room(self, headers, roomId):
        """
        结束所有课程
        :param headers:
        :type headers:
        :return:
        :rtype:
        """
        payload = {
            "roomId": roomId
        }
        url = "http://stable-fe-pos-nt.qa.fiture.com/bff-api/cp-cms.nt/api/room/end"
        log.info(f"查询条件: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        resp = resp.json()
        log.debug(f"结束房间:, {resp}")

    def end_room_end(self, roomName):
        """结束所有约练房间"""
        headers = {
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5MG1SMjJXU1JHTGZYZnMyTkNsU2piWEFkWXFMaG1LeEFacHpUTnhXak04In0.eyJqdGkiOiJiNmFkZTc1Yy1jMjg3LTQzMzUtOGQ5Zi01MmM3YWQ0Yjk1ZDgiLCJleHAiOjE2ODc3NDk4MjYsIm5iZiI6MCwiaWF0IjoxNjg3NjYzNDI2LCJpc3MiOiJodHRwczovL2tleWNsb2FrLmRldi5maXR1cmUuY29tL2F1dGgvcmVhbG1zL2ZpdHVyZSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI1NjRiMTQzYy00ODhlLTRlNDAtODgxOS1mNDE2ZTZiZDAzMGYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJwb3MiLCJub25jZSI6ImE0YjU0MTI1LWRhZWMtNDcyYy1iMDhkLTBlMjQ5OTY4OGNmMCIsImF1dGhfdGltZSI6MTY4NzE2NTcxOSwic2Vzc2lvbl9zdGF0ZSI6ImQ0NDY0OGU4LTBhZWMtNDI2Yi1hZjE5LTJjODE3NGJjOWEyMCIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiLlv5flvLog5LqOIiwicHJlZmVycmVkX3VzZXJuYW1lIjoieXpxIiwiZ2l2ZW5fbmFtZSI6IuW_l-W8uiIsImZhbWlseV9uYW1lIjoi5LqOIiwiZW1haWwiOiJ5enFAZml0dXJlLmNvbSJ9.DX8nTJGwxN2kQo32h9IR02cB2XUxF-HZF0znJQn-xMDVUlq_XZKCONKczL48Ew2ywnN8L64X0h-FNXQdXL6WjOvCJidjkv7HbhENzTgopZOPj91Qp_LjEdgRBW207cOB4eq2roszzMBLwxCNmbVcN-wYQHgv2uqA08tYRYOPsFFX7lOXl2R73lJexwzxDXP7HiwxzmNGz7WmEqUvNeDgDh7mYZMEyG46FByM4QEorPE0_9sMNnoQAiLTKS6eeodSgpXqpQFzSAnzJWVS2Y_XVSSKe1xriZiFkacfoHWVDWeXKAmf5zyWTClTlEvpc0M9qs-bkROyvwHP2a1KEwG5jw",
                "X-NT-App-Meta": json.dumps(
                {"appId": "h1t86b7s1igw7qothtkxzn0c", "appName": "fe-pos", "discoverName": "fe-pos.nt",
                 "deployQualifier": "stable", "deployId": "h1t86b7ypstcbae0jgmt9pub"})
        }
        roomIds = self.search_room(headers, roomName)
        for r in roomIds:
            self.end_room(headers, r)


if __name__ == "__main__":
    # sessions = TAAS().getSessions(accountCount=10000, ignoreExpire=False)
    # sessions = list(filter(lambda s: s.get("accountId") == "1427889425896157186", sessions))
    # print(sessions)
    # sessions = TAAS().forceUpdate()
    # print(sessions)
    sessions = TAAS().createSessionsQueue()
    print(sessions)
    # resp = TAAS().createSessionsQueue()
    # print(resp)
    # print(len(sessions))
    # TAAS().forceUpdate()

    # users = TAAS().getUsers()
    # users = list(filter(lambda u: u.get("accountId") == "1427889425896157186", users))
    # print(users)
    # TAAS().end_room_end('性能测试')

# echo "FILE=task_together_v2.py" > .env && docker-compose up --scale worker=20 --scale master=0    10.104.2.140执行
#
# echo "FILE=task_together_v2.py" > .env && docker-compose up --scale worker=20   10.120.0.14执行
