#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

from pathlib import Path
from hex_flow_core import LaunchConfig, NodeConfig

EXAMPLES_DIR = Path(__file__).resolve().parent

config = LaunchConfig(
    local_only=True,
    enable_tui=True,
    log_to_file=True,
    save_path="/tmp/my_hex_flow.launch.yml",
)

nodes: dict[str, NodeConfig] = {}

for i in range(8):
    node_name = f"test_pub_cmd_{i}"
    nodes[node_name] = NodeConfig(
        name=node_name,
        run_cmd=f"python {EXAMPLES_DIR}/test_pub_cmd.py",
        build_cmd="pip install -e ../hex_flow_core",
        required=True,
        hidden=True,
        remap_dict={
            "test/cmd": "test/cmd",
        },
        env_dict={
            "RUST_LOG": "info",
            "PRINT_LOG": "false",
        },
    )

for i in range(6):
    node_name = f"test_pub_img_{i}"
    nodes[node_name] = NodeConfig(
        name=node_name,
        run_cmd=f"python {EXAMPLES_DIR}/test_pub_img.py",
        build_cmd="pip install -e ../hex_flow_core",
        required=True,
        hidden=True,
        remap_dict={
            "test/img": "test/img",
        },
        env_dict={
            "RUST_LOG": "info",
            "PRINT_LOG": "false",
        },
    )

nodes["test_sub"] = NodeConfig(
    name="test_sub",
    run_cmd=f"python {EXAMPLES_DIR}/test_sub.py",
    build_cmd="pip install -e ../hex_flow_core",
    required=True,
    remap_dict={
        "test/cmd": "test/cmd",
        "test/img": "test/img",
    },
    env_dict={
        "RUST_LOG": "info",
    },
)

config.set_nodes(nodes)
print(config.export())
