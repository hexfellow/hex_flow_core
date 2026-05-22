#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import time, traceback
import numpy as np
from hex_util_runtime import HexRate
from hex_util_runtime import get_env_bool
from hex_flow_core import NodeCallback


def real_main(log_flag: bool, node: NodeCallback, data: np.ndarray):
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


def sim_main(log_flag: bool, node: NodeCallback, data: np.ndarray):
    cnt = 0
    start_ts_ns = None
    rate = 50
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
                    node.pub("test/img", data.tobytes())
                    cnt += 1
                    if cnt % rate == 0:
                        if start_ts_ns is None:
                            start_ts_ns = cur_tick
                        else:
                            elapsed_s = 1e-9 * (cur_tick - start_ts_ns)
                            if log_flag:
                                node.info(
                                    f"sent {cnt} images ({rate / elapsed_s:.1f} img/s)"
                                )
                            start_ts_ns = cur_tick
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


def main():
    log_flag = get_env_bool("PRINT_LOG")
    sim_flag = get_env_bool("SIM_TICK")
    node = NodeCallback("test_pub_img")
    node.start()
    node.create_pub("test/img")

    data = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
    if log_flag:
        node.info("publishing to test/img at ~50 Hz")

    if sim_flag:
        sim_main(log_flag, node, data)
    else:
        real_main(log_flag, node, data)


if __name__ == "__main__":
    main()
