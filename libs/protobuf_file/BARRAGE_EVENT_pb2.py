# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: BARRAGE_EVENT.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x42\x41RRAGE_EVENT.proto\x12\x08protobuf\":\n\x0c\x42\x61rrageEvent\x12*\n\x08\x63ontents\x18\x01 \x03(\x0b\x32\x18.protobuf.BarrageContent\"\x9f\x01\n\x0e\x42\x61rrageContent\x12\x10\n\x08serialId\x18\x01 \x01(\x03\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x0c\n\x04text\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\x05\x12%\n\x06sender\x18\x05 \x01(\x0b\x32\x15.protobuf.BarrageUser\x12\'\n\x08receiver\x18\x06 \x01(\x0b\x32\x15.protobuf.BarrageUser\"Q\n\x0b\x42\x61rrageUser\x12\x0e\n\x06userId\x18\x01 \x01(\x03\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x0e\n\x06\x61vatar\x18\x03 \x01(\t\x12\x10\n\x08userRole\x18\x04 \x01(\tB>\n)com.fiture.barrage.barrage.mq.event.protoB\x11\x42\x61rrageEventProtob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'BARRAGE_EVENT_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n)com.fiture.barrage.barrage.mq.event.protoB\021BarrageEventProto'
  _globals['_BARRAGEEVENT']._serialized_start=33
  _globals['_BARRAGEEVENT']._serialized_end=91
  _globals['_BARRAGECONTENT']._serialized_start=94
  _globals['_BARRAGECONTENT']._serialized_end=253
  _globals['_BARRAGEUSER']._serialized_start=255
  _globals['_BARRAGEUSER']._serialized_end=336
# @@protoc_insertion_point(module_scope)
