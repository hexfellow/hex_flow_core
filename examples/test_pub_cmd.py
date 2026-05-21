#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import time, traceback
import numpy as np
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
    start = time.perf_counter()
    pub_intv_ns = int(1e9 / 1000)
    last_pub_ts_ns = -1

    try:
        while True:
            time.sleep(1e-5)
            if node.cur_ts_ns - last_pub_ts_ns < pub_intv_ns:
                continue
            last_pub_ts_ns = node.cur_ts_ns

            node.pub("test/cmd", data.tobytes())

            cnt += 1
            if cnt % 1000 == 0:
                elapsed = time.perf_counter() - start
                if log_flag:
                    node.info(
                        f"sent {cnt} commands ({cnt / elapsed:.1f} cmd/s)")
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
