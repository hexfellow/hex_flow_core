#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-05-21
################################################################

import traceback
from hex_util_runtime import HexRate, ns_now
from hex_util_runtime import get_env_bool
from hex_util_msg.builder_basic import build_hex_ts_ns
from hex_flow_core import NodeCallback


def main():
    log_flag = get_env_bool("PRINT_LOG")
    node = NodeCallback("hex_flow_tick", sub_tick=False)
    node.start()
    node.create_pub("tick")

    cnt = 0
    start_ts_ns = ns_now()
    rate = HexRate(2000)
    try:
        while True:
            rate.sleep()
            cnt += 1
            tick_ts_ns = ns_now()
            node.pub("tick", build_hex_ts_ns(tick_ts_ns))
            if cnt % 1000 == 0:
                elapsed_s = 1e-9 * (tick_ts_ns - start_ts_ns)
                if log_flag:
                    node.info(
                        f"sent {cnt} ticks ({1000.0 / elapsed_s:.1f} tick/s)")
                start_ts_ns = tick_ts_ns
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
