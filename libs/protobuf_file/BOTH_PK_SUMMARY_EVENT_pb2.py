# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: BOTH_PK_SUMMARY_EVENT.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1b\x42OTH_PK_SUMMARY_EVENT.proto\x12\x08protobuf\"_\n\x12\x42othPkSummaryEvent\x12\x1f\n\x06groups\x18\x01 \x03(\x0b\x32\x0f.protobuf.Group\x12(\n\x05users\x18\x02 \x03(\x0b\x32\x19.protobuf.PkUserBasicInfo\"e\n\x05Group\x12\x11\n\tgroupCode\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x12\x11\n\tencourage\x18\x03 \x01(\t\x12\'\n\trankUsers\x18\x04 \x03(\x0b\x32\x14.protobuf.PkRankUser\"\x84\x01\n\nPkRankUser\x12\x11\n\taccountId\x18\x01 \x01(\x03\x12\x10\n\x08position\x18\x02 \x01(\x05\x12\x10\n\x08username\x18\x03 \x01(\t\x12\x0e\n\x06\x61vatar\x18\x04 \x01(\t\x12\x0e\n\x06gender\x18\x05 \x01(\t\x12\x10\n\x08location\x18\x06 \x01(\t\x12\r\n\x05\x63ount\x18\x07 \x01(\x05\"3\n\x0fPkUserBasicInfo\x12\x11\n\taccountId\x18\x01 \x01(\x03\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\x42@\n%com.fiture.recording.room.event.protoB\x17\x42othPkSummaryEventProtob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'BOTH_PK_SUMMARY_EVENT_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n%com.fiture.recording.room.event.protoB\027BothPkSummaryEventProto'
  _globals['_BOTHPKSUMMARYEVENT']._serialized_start=41
  _globals['_BOTHPKSUMMARYEVENT']._serialized_end=136
  _globals['_GROUP']._serialized_start=138
  _globals['_GROUP']._serialized_end=239
  _globals['_PKRANKUSER']._serialized_start=242
  _globals['_PKRANKUSER']._serialized_end=374
  _globals['_PKUSERBASICINFO']._serialized_start=376
  _globals['_PKUSERBASICINFO']._serialized_end=427
# @@protoc_insertion_point(module_scope)