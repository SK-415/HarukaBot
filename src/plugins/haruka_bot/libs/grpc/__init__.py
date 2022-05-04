import hashlib
import random
import grpc.aio

from loguru import logger
from grpc import RpcError
from grpc_status import rpc_status
from google.protobuf.json_format import MessageToDict


from .bilibili.metadata.metadata_pb2 import Metadata
from .bilibili.metadata.device.device_pb2 import Device
from .bilibili.metadata.locale.locale_pb2 import Locale
from .bilibili.metadata.network.network_pb2 import Network
from .bilibili.live.app.room.v1.room_pb2 import GetStudioListReq
from .bilibili.app.dynamic.v2.dynamic_pb2_grpc import DynamicStub
from .bilibili.live.app.room.v1.room_pb2_grpc import StudioListStub
from .bilibili.app.dynamic.v2.dynamic_pb2 import (
    DynAllReq,
    DynamicType,
    DynSpaceReq,
    DynMixUpListViewMoreReq,
)

server = "grpc.biliapi.net"


def fakebuvid():
    mac_list = []
    for _ in range(1, 7):
        rand_str = "".join(random.sample("0123456789abcdef", 2))
        mac_list.append(rand_str)
    rand_mac = ":".join(mac_list)
    md5 = hashlib.md5()
    md5.update(rand_mac.encode())
    md5_mac_str = md5.hexdigest()
    md5_mac = list(md5_mac_str)
    fake_mac = ("XY" + md5_mac[2] + md5_mac[12] + md5_mac[22] + md5_mac_str).upper()
    return fake_mac


def make_metadata():
    buvid = fakebuvid()
    return (
        (
            "x-bili-device-bin",
            Device(
                build=6550400,
                buvid=buvid,
                mobi_app="android",
                platform="android",
                device="phone",
                channel="bili",
            ).SerializeToString(),
        ),
        (
            "x-bili-local-bin",
            Locale().SerializeToString(),
        ),
        (
            "x-bili-metadata-bin",
            Metadata(
                # access_key=get_token(),
                mobi_app="android",
                device="phone",
                build=6550400,
                channel="bili",
                buvid=buvid,
                platform="android",
            ).SerializeToString(),
        ),
        ("x-bili-network-bin", Network(type="WIFI").SerializeToString()),
        # ("authorization", f"identify_v1 {get_token()}".encode()),
    )


async def grpc_dyn_get(uid: int):
    async with grpc.aio.secure_channel(server, grpc.ssl_channel_credentials()) as channel:
        stub = DynamicStub(channel)
        req = DynSpaceReq(host_uid=int(uid))
        meta = make_metadata()
        try:
            resp = await stub.DynSpace(req, metadata=meta)
        except RpcError as e:
            status = rpc_status.from_call(e)
            logger.error(status)
        return resp


async def grpc_dynall_get():
    async with grpc.aio.secure_channel(server, grpc.ssl_channel_credentials()) as channel:
        stub = DynamicStub(channel)
        req = DynAllReq()
        meta = make_metadata()
        try:
            resp = await stub.DynAll(req, metadata=meta)
        except RpcError as e:
            status = rpc_status.from_call(e)
            logger.error(status)

        exclude_list = [DynamicType.ad, DynamicType.live, DynamicType.live_rcmd]
        dynlist = filter(
            lambda x: x.card_type not in exclude_list,
            resp.dynamic_list.list,
        )
        return list(dynlist)


async def grpc_uplist_get():
    async with grpc.aio.secure_channel(server, grpc.ssl_channel_credentials()) as channel:
        stub = DynamicStub(channel)
        req = DynMixUpListViewMoreReq(sort_type=1)
        meta = make_metadata()
        try:
            resp = await stub.DynMixUpListViewMore(req, metadata=meta)
        except RpcError as e:
            status = rpc_status.from_call(e)
            logger.error(status)
        return MessageToDict(resp, preserving_proto_field_name=True)


async def grpc_studio_get(room_id):
    async with grpc.aio.secure_channel(server, grpc.ssl_channel_credentials()) as channel:
        stub = StudioListStub(channel)
        req = GetStudioListReq(room_id=int(room_id))
        meta = make_metadata()
        try:
            resp = await stub.GetStudioList(req, metadata=meta)
        except RpcError as e:
            status = rpc_status.from_call(e)
            logger.error(status)
        return resp
