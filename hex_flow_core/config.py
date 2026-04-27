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
        hidden: bool = False,
        remap_dict: dict[str, str] | None = None,
        env_dict: dict[str, str] | None = None,
    ):
        self.__name = name
        self.__build_cmd = build_cmd
        self.__run_cmd = run_cmd
        self.__required = required
        self.__hidden = hidden
        self.__remap_dict = remap_dict if remap_dict is not None else {}
        self.__env_dict = env_dict if env_dict is not None else {}

    def get_name(self) -> str:
        return self.__name

    def get_required(self) -> bool:
        return self.__required

    def get_hidden(self) -> bool:
        return self.__hidden

    def get_remap_dict(self) -> dict[str, str]:
        return self.__remap_dict

    def get_env_dict(self) -> dict[str, str]:
        return self.__env_dict

    def set_name(self, name: str):
        self.__name = name

    def set_required(self, required: bool):
        self.__required = required

    def set_hidden(self, hidden: bool):
        self.__hidden = hidden

    def set_remap_dict(self, remap_dict: dict[str, str], update: bool = False):
        if update:
            self.__remap_dict.update(remap_dict)
        else:
            self.__remap_dict = remap_dict

    def set_env_dict(self, env_dict: dict[str, str], update: bool = False):
        if update:
            self.__env_dict.update(env_dict)
        else:
            self.__env_dict = env_dict

    def update(self, other: "NodeConfig"):
        self.__name = other.__name
        self.__required = other.__required
        self.__hidden = other.__hidden
        if other.__build_cmd:
            self.__build_cmd = other.__build_cmd
        if other.__run_cmd:
            self.__run_cmd = other.__run_cmd
        self.__remap_dict.update(other.__remap_dict)
        self.__env_dict.update(other.__env_dict)

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

    @staticmethod
    def from_dict(data: dict) -> "NodeConfig":
        return NodeConfig(
            name=data["name"],
            run_cmd=data["run"],
            build_cmd=data.get("build", ""),
            required=data["required"],
            remap_dict=data.get("remap", {}),
            env_dict=data.get("env", {}),
        )


class LaunchConfig:

    def __init__(
        self,
        local_only: bool = False,
        enable_tui: bool = False,
        log_to_file: bool = False,
        clear_old: bool = True,
        save_path: str = "/tmp/hex_flow.launch.yml",
    ):
        self.__local_only = local_only
        self.__enable_tui = enable_tui
        self.__log_to_file = log_to_file and enable_tui
        self.__clear_old = clear_old
        self.__node_map: dict[str, NodeConfig] = {}
        self.__save_path = save_path

    def get_path(self) -> str:
        return self.__save_path

    def get_node(self, name: str) -> NodeConfig:
        return self.__node_map.get(name, None)

    def get_node_names(self) -> list[str]:
        return list(self.__node_map.keys())

    def set_node(self,
                 name: str,
                 node_config: NodeConfig,
                 update: bool = False):
        node_config.set_name(name)
        if update and name in self.__node_map:
            self.__node_map[name].update(node_config)
        else:
            self.__node_map[name] = node_config

    def set_nodes(self, node_map: dict[str, NodeConfig], update: bool = False):
        if update:
            self.__node_map.update(node_map)
        else:
            self.__node_map = node_map

    def merge(self, other: "LaunchConfig"):
        self.__node_map.update(other.__node_map)
        self.__local_only = self.__local_only and other.__local_only
        self.__enable_tui = self.__enable_tui or other.__enable_tui
        self.__log_to_file = self.__log_to_file or other.__log_to_file

    def export(self) -> str:
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
            "tui-log-to-file": self.__log_to_file,
            "skip-killing-old-zenohd": not self.__clear_old,
        }
        if self.__node_map:
            data["nodes"] = [n.to_dict() for n in self.__node_map.values()]

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

    @staticmethod
    def from_yml(path: str, save_path: str = None) -> "LaunchConfig":
        with open(path, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        router = data.get("router", {})
        multicast = router.get("multicast", {})
        local_only = multicast.get("address") == "127.0.0.1"

        launcher = data.get("launcher", {})
        launch_config = LaunchConfig(
            local_only=local_only,
            enable_tui=not launcher.get("disable-tui", True),
            log_to_file=launcher.get("tui-log-to-file", False),
            save_path=path if save_path is None else save_path,
        )
        for node in data.get("nodes", []):
            launch_config.set_node(
                node["name"],
                NodeConfig.from_dict(node),
                update=True,
            )
        return launch_config
