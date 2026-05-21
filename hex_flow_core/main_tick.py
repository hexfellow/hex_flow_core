#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-05-21
################################################################

import traceback
from hex_util_runtime import HexRate, ns_now
from hex_util_msg.builder_basic import build_hex_ts_ns
from hex_flow_core import NodeCallback


def main():
    node = NodeCallback("hex_flow_tick", sub_tick=False)
    node.start()
    node.create_pub("tick")
    
    rate = HexRate(2000)
    try:
        while True:
            rate.sleep()
            node.pub("tick", build_hex_ts_ns(ns_now()))
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
