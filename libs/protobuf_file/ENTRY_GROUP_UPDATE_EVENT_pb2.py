# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ENTRY_GROUP_UPDATE_EVENT.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x45NTRY_GROUP_UPDATE_EVENT.proto\x12\x08protobuf\"N\n\x15\x45ntryGroupUpdateEvent\x12\x35\n\x07players\x18\x01 \x03(\x0b\x32$.protobuf.EntryGroupUpdateRoomPlayer\"\x90\x01\n\x1a\x45ntryGroupUpdateRoomPlayer\x12\x11\n\taccountId\x18\x01 \x01(\x03\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x0e\n\x06\x61vatar\x18\x03 \x01(\t\x12\x10\n\x08location\x18\x04 \x01(\t\x12\x0b\n\x03\x61ge\x18\x05 \x01(\x05\x12\x0e\n\x06gender\x18\x06 \x01(\t\x12\x0e\n\x06status\x18\x07 \x01(\tBC\n%com.fiture.recording.room.event.protoB\x1a\x45ntryGroupUpdateEventProtob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ENTRY_GROUP_UPDATE_EVENT_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n%com.fiture.recording.room.event.protoB\032EntryGroupUpdateEventProto'
  _globals['_ENTRYGROUPUPDATEEVENT']._serialized_start=44
  _globals['_ENTRYGROUPUPDATEEVENT']._serialized_end=122
  _globals['_ENTRYGROUPUPDATEROOMPLAYER']._serialized_start=125
  _globals['_ENTRYGROUPUPDATEROOMPLAYER']._serialized_end=269
# @@protoc_insertion_point(module_scope)
