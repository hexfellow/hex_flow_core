#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import time, traceback
from hex_flow_core import NodeCallback

CMD_PAYLOAD_SIZE = 81920  # 10240 * uint64
IMG_PAYLOAD_SIZE = 2764800  # 720 * 1280 * 3 * uint8


def main():
    node = NodeCallback("test_sub")
    node.start()

    cmd_count = 0
    img_count = 0
    cmd_window_start = time.perf_counter()
    img_window_start = time.perf_counter()

    def cmd_listener(sample):
        nonlocal cmd_count, cmd_window_start

        payload = sample.payload.to_bytes()
        if len(payload) != CMD_PAYLOAD_SIZE:
            node.warn(f"unexpected cmd payload size: {len(payload)}")

        cmd_count += 1
        if cmd_count % 1000 == 0:
            now = time.perf_counter()
            elapsed = now - cmd_window_start
            cmd_window_start = now
            node.info(f"received {cmd_count} commands "
                      f"({1000.0 / elapsed:.1f} cmd/s over last 1000)")

    def img_listener(sample):
        nonlocal img_count, img_window_start

        payload = sample.payload.to_bytes()
        if len(payload) != IMG_PAYLOAD_SIZE:
            node.warn(f"unexpected img payload size: {len(payload)}")

        img_count += 1
        if img_count % 200 == 0:
            now = time.perf_counter()
            elapsed = now - img_window_start
            img_window_start = now
            node.info(f"received {img_count} images "
                      f"({200.0 / elapsed:.1f} img/s over last 200)")

    node.create_sub("test/cmd", cmd_listener)
    node.create_sub("test/img", img_listener)

    node.info("subscribing to test/cmd and test/img")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        node.stop()


if __name__ == "__main__":
    main()
