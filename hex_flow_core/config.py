#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-22
################################################################

import os, yaml


class NodeConfig:

    def __init__(
        self,
        name: str = "",
        build_cmd: str = "",
        run_cmd: str = "",
        required: bool = True,
        remap_dict: dict[str, str] = {},
        env_dict: dict[str, str] = {},
    ):
        self.__name = name
        self.__build_cmd = build_cmd
        self.__run_cmd = run_cmd
        self.__required = required
        self.__remap_dict = remap_dict
        self.__env_dict = env_dict

    def set_name(self, name: str):
        self.__name = name

    def to_dict(self) -> dict:
        d: dict = {"name": self.__name, "run": self.__run_cmd}
        if self.__build_cmd:
            d["build"] = self.__build_cmd
        d["required"] = self.__required
        if self.__remap_dict:
            d["remap"] = dict(self.__remap_dict)
        if self.__env_dict:
            d["env"] = dict(self.__env_dict)
        return d


class LaunchConfig:

    def __init__(
        self,
        local_only: bool = False,
        enable_tui: bool = False,
        log_to_file: bool = False,
        save_path: str = "/tmp/hex_flow_launch.yml",
    ):
        self.__local_only = local_only
        self.__enable_tui = enable_tui
        self.__log_to_file = log_to_file and enable_tui
        self.__node_list: list[NodeConfig] = []
        self.__save_path = save_path

    def get_path(self) -> str:
        return self.__save_path

    def save(self) -> str:
        data: dict = {}
        if self.__local_only:
            data["router"] = {
                "multicast": {
                    "address": "127.0.0.1",
                    "interface": "auto",
                }
            }
        data["launcher"] = {
            "disable-tui": not self.__enable_tui,
            "log-to-file": self.__log_to_file,
        }
        if self.__node_list:
            data["nodes"] = [n.to_dict() for n in self.__node_list]

        parent = os.path.dirname(self.__save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.__save_path, "w") as f:
            yaml.dump(data,
                      f,
                      default_flow_style=False,
                      allow_unicode=True,
                      sort_keys=False)
        return self.__save_path

    def add(self, node_map: dict[str, NodeConfig]):
        for name, node_config in node_map.items():
            node_config.set_name(name)
            self.__node_list.append(node_config)

    def merge(self, other: "LaunchConfig"):
        self.__node_list.extend(other.__node_list)
        self.__local_only = self.__local_only and other.__local_only
        self.__enable_tui = self.__enable_tui or other.__enable_tui
        self.__log_to_file = self.__log_to_file or other.__log_to_file
