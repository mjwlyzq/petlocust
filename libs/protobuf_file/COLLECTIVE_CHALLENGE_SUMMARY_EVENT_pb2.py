# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: COLLECTIVE_CHALLENGE_SUMMARY_EVENT.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n(COLLECTIVE_CHALLENGE_SUMMARY_EVENT.proto\x12\x08protobuf\"\xbf\x01\n\x1f\x43ollectiveChallengeSummaryEvent\x12\x17\n\x0f\x63hallengeTarget\x18\x01 \x01(\x05\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x12\x11\n\tencourage\x18\x03 \x01(\t\x12/\n\trankUsers\x18\x04 \x03(\x0b\x32\x1c.protobuf.CollectiveRankUser\x12\x30\n\x05users\x18\x05 \x03(\x0b\x32!.protobuf.CollectiveUserBasicInfo\"\x8c\x01\n\x12\x43ollectiveRankUser\x12\x11\n\taccountId\x18\x01 \x01(\x03\x12\x10\n\x08position\x18\x02 \x01(\x05\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x0e\n\x06\x61vatar\x18\x04 \x01(\t\x12\x0e\n\x06gender\x18\x05 \x01(\t\x12\x10\n\x08location\x18\x06 \x01(\t\x12\r\n\x05\x63ount\x18\x07 \x01(\x05\";\n\x17\x43ollectiveUserBasicInfo\x12\x11\n\taccountId\x18\x01 \x01(\x03\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x42M\n%com.fiture.recording.room.event.protoB$CollectiveChallengeSummaryEventProtob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'COLLECTIVE_CHALLENGE_SUMMARY_EVENT_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n%com.fiture.recording.room.event.protoB$CollectiveChallengeSummaryEventProto'
  _globals['_COLLECTIVECHALLENGESUMMARYEVENT']._serialized_start=55
  _globals['_COLLECTIVECHALLENGESUMMARYEVENT']._serialized_end=246
  _globals['_COLLECTIVERANKUSER']._serialized_start=249
  _globals['_COLLECTIVERANKUSER']._serialized_end=389
  _globals['_COLLECTIVEUSERBASICINFO']._serialized_start=391
  _globals['_COLLECTIVEUSERBASICINFO']._serialized_end=450
# @@protoc_insertion_point(module_scope)
