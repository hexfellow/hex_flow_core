#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import os, time, traceback
import numpy as np
from hex_util_runtime import HexRate
from hex_flow_core import NodeCallback


def parse_env_bool(env_name: str, default: str = "false") -> bool:
    return os.getenv(env_name, default).lower() in ["true", "1", "yes", "y"]


def main():
    log_flag = parse_env_bool("PRINT_LOG", "false")
    node = NodeCallback("test_pub_img")
    node.start()
    node.create_pub("test/img")

    data = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
    if log_flag:
        node.info("publishing to test/img at ~50 Hz")

    cnt = 0
    start = time.perf_counter()
    rate = HexRate(50)

    try:
        while True:
            rate.sleep()
            node.pub("test/img", data.tobytes())

            cnt += 1
            if cnt % 50 == 0:
                elapsed = time.perf_counter() - start
                if log_flag:
                    node.info(f"sent {cnt} images ({cnt / elapsed:.1f} img/s)")
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
