#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import time, traceback
import numpy as np
from hex_util_runtime import ns_now
from hex_util_runtime import get_env_bool
from hex_flow_core import NodeCallback


def main():
    log_flag = get_env_bool("PRINT_LOG")
    node = NodeCallback("test_pub_cmd")
    node.start()
    node.create_pub("test/cmd")

    data = np.random.randint(0, 1000000, size=10240, dtype=np.uint64)
    if log_flag:
        node.info("publishing to test/cmd at ~1000 Hz")

    cnt = 0
    start_ts_ns = None
    rate = 1000
    intv_ns = int(1e9 / rate)
    trig_ts = -1

    try:
        while True:
            time.sleep(1e-5)
            tick = node.get_tick()
            while tick is not None:
                cur_tick, tick = tick, node.get_tick()
                is_trig, trig_ts = node.tick_trig(trig_ts, cur_tick, intv_ns)
                if is_trig:
                    node.pub("test/cmd", data.tobytes())
                    cnt += 1
                    if cnt % rate == 0:
                        if start_ts_ns is None:
                            start_ts_ns = cur_tick
                        else:
                            elapsed_s = 1e-9 * (cur_tick - start_ts_ns)
                            if log_flag:
                                node.info(
                                    f"sent {cnt} commands ({rate / elapsed_s:.1f} cmd/s)"
                                )
                            start_ts_ns = cur_tick
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
