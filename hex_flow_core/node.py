#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import os, json
import envlog, logging
import zenoh
from typing import Callable, Optional
from collections import deque
from hex_util_runtime import deque_helper
from hex_util_msg.builder_basic import parse_hex_ts_ns

JITTER_NS = 250_000


class NodeCallback:

    def __init__(self, name: str = "unknown", sub_tick: bool = True):
        self.__name = os.getenv("HEX_FLOW_NODE_NAME", name)
        self.__remap = json.loads(os.getenv("HEX_FLOW_REMAP", "{}"))

        envlog.init(log_spec=os.getenv("RUST_LOG", "info"))
        self.__logger = logging.getLogger(self.__name)

        self.__zenoh_cfg = zenoh.Config()
        self.__zenoh_cfg.insert_json5("mode", '"client"')

        self.__session: Optional[zenoh.Session] = None
        self.__pubs: dict[str, zenoh.Publisher] = {}
        self.__subs: list = []
        self.__working = False

        self.__sub_tick = sub_tick
        self.__tick_dq: deque = deque(maxlen=1000)

    def _remap(self, topic: str) -> str:
        return self.__remap.get(topic, topic)

    # ---- lifecycle ----

    def start(self):
        if self.__working:
            return

        self.__session = zenoh.open(self.__zenoh_cfg)
        self.__session.put(
            f"hfmd/nodes/{self.__session.zid()}/node_name",
            self.__name.encode(),
        )

        self.__working = True
        self.info(f"node '{self.__name}' started")

        if self.__sub_tick:
            # init tick subscriber
            tick_topic = self._remap("tick")
            sub = self.__session.declare_subscriber(tick_topic,
                                                    self.__tick_listener)
            self.__subs.append(sub)

    def __tick_listener(self, sample):
        self.__tick_dq.append(sample.payload)

    def get_tick(self, latest: bool = False) -> Optional[int]:
        if not self.__sub_tick:
            print("This node does not support tick subscriber")
            return None
        sample = deque_helper(self.__tick_dq, latest=latest)
        if sample is None:
            return None
        msg = parse_hex_ts_ns(sample.to_bytes())
        return msg["ts_ns"]

    @staticmethod
    def tick_trig(trig_ts: int, cur_tick: int, intv_ns: int) -> [bool, int]:
        jitter_trig_ts = trig_ts - JITTER_NS
        if jitter_trig_ts < cur_tick:
            add_num = (cur_tick - jitter_trig_ts) // intv_ns + 1
            return True, trig_ts + add_num * intv_ns
        return False, trig_ts

    def stop(self):
        if not self.__working:
            return

        self.__working = False
        for sub in self.__subs:
            sub.undeclare()
        self.__subs.clear()
        for pub in self.__pubs.values():
            pub.undeclare()
        self.__pubs.clear()
        if self.__session is not None:
            self.__session.close()
            self.__session = None
        self.info(f"node '{self.__name}' stopped")

    def is_working(self) -> bool:
        return self.__working

    # ---- pub / sub ----

    def create_pub(self, topic: str):
        real_topic = self._remap(topic)
        if real_topic not in self.__pubs:
            self.__pubs[real_topic] = self.__session.declare_publisher(
                real_topic)

    def create_sub(self, topic: str, callback: Callable):
        real_topic = self._remap(topic)
        sub = self.__session.declare_subscriber(real_topic, callback)
        self.__subs.append(sub)

    def pub(self, topic: str, data: bytes):
        real_topic = self._remap(topic)
        publisher = self.__pubs.get(real_topic, None)
        if publisher is None:
            self.warn(f"no publisher for topic '{topic}' (real: {real_topic})")
            return
        publisher.put(data)

    # ---- logging ----

    def debug(self, message: str):
        self.__logger.debug(message)

    def info(self, message: str):
        self.__logger.info(message)

    def warn(self, message: str):
        self.__logger.warning(message)

    def error(self, message: str):
        self.__logger.error(message)

    def fatal(self, message: str):
        self.__logger.fatal(message)


class Node(NodeCallback):

    def __init__(self, name: str = "unknown"):
        super().__init__(name)
        self.__dq_map: dict[str, deque] = {}

    def create_sub(self, topic: str, maxlen: int = 10):
        real_topic = self._remap(topic)
        dq: deque = deque(maxlen=maxlen)
        self.__dq_map[real_topic] = dq

        def _enqueue(sample):
            dq.append(sample.payload.to_bytes())

        super().create_sub(topic, _enqueue)

    def get(self, topic: str, latest: bool = False) -> Optional[bytes]:
        real_topic = self._remap(topic)
        dq = self.__dq_map.get(real_topic, None)
        if dq is None:
            self.warn(f"no queue for topic '{topic}' (real: {real_topic})")
            return None
        return deque_helper(dq, latest)
