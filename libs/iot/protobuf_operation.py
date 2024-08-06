import json
import random
import time
import uuid

from libs.logger import log
from libs.protobuf_file import ENTRY_GROUPING_EVENT_pb2, START_ROOM_EVENT_pb2, \
    ROOM_TIMING_LINE_SYNC_EVENT_pb2, PLAYER_TRAINING_MOMENT_EVENT_pb2


class ProtoBufQuickBurning:
    def __init__(self, client=None, protoc=None, kwargs=None):
        # 创建一个Person实例
        self.client = client
        self.person = protoc
        self.kwargs = kwargs

    def default_filed(self, tags):
        # 创建protobuf消息
        self.person = self.person.Protocol()
        # self.person.version = 1
        # self.person.srcApp = 2
        # self.person.dstApp = 3
        log.info(f'获取到accountId和roomId={self.kwargs}')
        self.person.srcId = str(self.kwargs.get('accountId'))
        self.person.dstId = str(self.kwargs.get('roomId'))
        # self.person.msgCode = 'PLAYER_ENTRY_EVENT'
        self.person.tags = tags
        # self.person.feature = 1
        self.person.msgId = uuid.uuid4().hex[:16]
        self.person.ts = int(time.time())
        self.person.priority = 100
        self.person.contentType = 'application/x-protobuf'
        # self.person.ext = 1
        # self.person.payload = json.dumps({}).encode('utf-8')

    def return_person(self):
        return self.person

    def room_timing_line_sync_event(self):
        """
        时间轴进度同步
        :return:
        :rtype:
        """
        self.person = self.person.RoomTimingLineSyncEvent()

    def player_entry_event(self):
        """用户进入房间消息"""
        self.person = self.person.PlayerEnterEvent()

    def start_room_event_pb2(self):
        """房间开始"""
        self.person = self.person.StartRoomEvent()

    def entry_grouping_event(self):
        """入场分组完成消息"""
        self.person = self.person.EntryGroupingEvent()

    def entry_group_update_event(self):
        """入场分组组员变更消息"""
        self.person = self.person.EntryGroupUpdateRoomPlayer()

    def end_room_event(self):
        """房间结束"""
        self.person = self.person.EndRoomEvent()

    def coach_guide_detail_event(self):
        """教练发送巡场指导数据"""
        self.person = self.person.CoachGuideDetailEvent()

    def collective_challenge_show_players_event(self):
        """合力挑战准备下发挑战目标和展示玩家的消息"""
        self.person = self.person.CollectiveChallengeShowPlayersEvent()

    def pk_server_transfer_player_data_event(self):
        """PK(合力挑战、红蓝PK)服务端转发用户实时数据消息到房间"""
        self.person = self.person.CollectiveChallengePlayerDataEvent()

    def collective_challenge_progress_event(self):
        """合力挑战进行中下发总挑战次数和鼓励语消息"""
        self.person = self.person.CollectiveChallengeProgressEvent()

    def collective_challenge_summary_event(self):
        """合力挑战总结页下发消息"""
        self.person = self.person.CollectiveChallengeSummaryEvent()

    def both_pk_grouping_event(self):
        """红蓝PK分组完成消息"""
        self.person = self.person.BothPkGroupingEvent()

    def both_pk_progress_event(self):
        """红蓝PK进行中下发总挑战次数和鼓励语消息"""
        self.person = self.person.BothPkProgressEvent()

    def both_pk_summary_event(self):
        """红蓝PK总结页下发消息"""
        self.person = self.person.BothPkSummaryEvent()

    def stage_show_result_event(self):
        """房间抢镜的计算结果"""
        self.person = self.person.StageShowResultEvent()

    def player_training_moment_event(self):
        """用户瞬时运动消息（每秒上报）"""
        self.person = self.person.PlayerTrainingMomentEvent()

    def player_high_five_event(self):
        """击掌结果上报"""
        self.person = self.person.PlayerHighFiveEvent()

    def mc_coach_report_skeleton_event(self):
        """教练通知骨骼点上报指令"""
        self.person = self.person.HostReportSkeletonEvent()

    def mc_coach_stop_report_skeleton_event(self):
        """教练通知骨骼点停止上报指令"""
        self.person = self.person.HostStopReportSkeletonEvent()

    def coach_skeleton_event(self):
        """web端显示骨骼点"""
        self.person = self.person.SkeletonDataEvent()

    def assign_stage_show_skeleton_event(self):
        """教练指定上镜"""
        self.person = self.person.SkeletonDataEvent()

    def barrage_event(self):
        """弹幕下发消息"""
        self.person = self.person.BarrageEvent()

    def coach_post_emoji_event(self):
        """教练发送表情"""
        self.person = self.person.CoachPostEmojiEvent()

    def send_online_player_event(self):
        """玩家退出发送房间在线玩家总数和15个玩家信息、当前退出玩家ID"""
        self.person = self.person.SendOnlinePlayerEvent()

    def entry_group_newly_created_event(self):
        """产生新的入场分组消息（新玩家中途进入且当前分组已满员的情况）"""
        self.person = self.person.EntryGroupingEvent()

    def to_str(self):
        getData = self.person.SerializeToString()
        return getData

    def to_obj(self, getStr):
        self.person.ParseFromString(getStr)
        return self.person

    def byte_length(self, getStr):
        return self.person.ParseFromString(getStr)


if __name__ == '__main__':
    # p = ProtoBufQuickBurning()
    # p.entry_grouping_event()
    # p.person.payload = json.dumps({"name": "yzq"}).encode(encoding='utf-8')
    c = b"\b\201\200\200\215\272\325\345\313\027\020\216\001\030G \206\r0\0018\001@\366\341\335\251\006J\r\b\001\020\002\031\000\000\000\000\000\000\b@P\205\240\376\367\325\327\274\351\027Z\022GROUP_PICK_STAR_PKb\006PK_INGh\206\001r\005SCORE\202\001\f\022\004STAR\032\004ITEM\202\001\r\022\004STAR\032\005TOTAL\202\001\016\022\004STAR\032\006MODULE\202\001\032\t\000\000\000\000\000\000Y@\022\005SCORE\032\bKEYFRAME\202\001 \t\000\000\000\000\000\000Y@\022\005SCORE\032\016KEYFRAME_TOTAL\212\001\026\n\aAWESOME\020\017\032\tREAL_TIME\222\001\t\b\017\022\005TOTAL\222\001\b\b\017\022\004ITEM\252\001\f\022\004STAR\032\004ITEM\252\001\r\022\004STAR\032\005TOTAL\252\001\016\022\004STAR\032\006MODULE\252\001\032\t\000\000\000\000\000\000Y@\022\005SCORE\032\bKEYFRAME\252\001 \t\000\000\000\000\000\000Y@\022\005SCORE\032\016KEYFRAME_TOTAL"
    # print(a)
    # p.to_obj()

    getObj = ProtoBufQuickBurning(protoc=PLAYER_TRAINING_MOMENT_EVENT_pb2)
    getObj.player_training_moment_event()
    # getObj.person.movementPerformance.movementId = 0
    # getObj.person.movementPerformance.repeats = 2
    # getObj.person.movementPerformance.rate = 3.0
    print(getObj.byte_length(c))
    # msgData = getObj.to_str()
    # print(msgData)
    msgData = getObj.to_obj(c)

    print(msgData)
    # playergroupTopic = msgData.groups.channels.get('topicSuffix')
    # print(f'入场分组完成消息，消息：{msgData.groups}, type={type(msgData.groups)}')
    # print(msgData.roomItemId)