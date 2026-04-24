#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import tempfile
import yaml
import pytest

from hex_flow_core.config import NodeConfig, LaunchConfig


# ───────────────────────── NodeConfig ─────────────────────────


class TestNodeConfigInit:

    def test_defaults(self):
        nc = NodeConfig()
        assert nc.get_name() == ""
        assert nc.get_required() is True
        assert nc.get_remap_dict() == {}
        assert nc.get_env_dict() == {}

    def test_mutable_defaults_are_independent(self):
        a = NodeConfig()
        b = NodeConfig()
        a.get_remap_dict()["x"] = "y"
        assert b.get_remap_dict() == {}

    def test_custom_values(self):
        nc = NodeConfig(
            name="n1",
            build_cmd="make",
            run_cmd="./run",
            required=False,
            remap_dict={"a": "b"},
            env_dict={"K": "V"},
        )
        assert nc.get_name() == "n1"
        assert nc.get_required() is False
        assert nc.get_remap_dict() == {"a": "b"}
        assert nc.get_env_dict() == {"K": "V"}


class TestNodeConfigSetters:

    def test_set_name(self):
        nc = NodeConfig()
        nc.set_name("foo")
        assert nc.get_name() == "foo"

    def test_set_required(self):
        nc = NodeConfig()
        nc.set_required(False)
        assert nc.get_required() is False

    def test_set_remap_dict_replace(self):
        nc = NodeConfig(remap_dict={"old": "val"})
        nc.set_remap_dict({"new": "val2"})
        assert nc.get_remap_dict() == {"new": "val2"}

    def test_set_remap_dict_update(self):
        nc = NodeConfig(remap_dict={"old": "val"})
        nc.set_remap_dict({"new": "val2"}, update=True)
        assert nc.get_remap_dict() == {"old": "val", "new": "val2"}

    def test_set_env_dict_replace(self):
        nc = NodeConfig(env_dict={"A": "1"})
        nc.set_env_dict({"B": "2"})
        assert nc.get_env_dict() == {"B": "2"}

    def test_set_env_dict_update(self):
        nc = NodeConfig(env_dict={"A": "1"})
        nc.set_env_dict({"B": "2"}, update=True)
        assert nc.get_env_dict() == {"A": "1", "B": "2"}


class TestNodeConfigUpdate:

    def test_merges_all_fields(self):
        base = NodeConfig(
            name="base",
            build_cmd="make",
            run_cmd="./base",
            required=True,
            remap_dict={"a": "1"},
            env_dict={"X": "1"},
        )
        other = NodeConfig(
            name="overlay",
            build_cmd="cmake",
            run_cmd="./overlay",
            required=False,
            remap_dict={"b": "2"},
            env_dict={"Y": "2"},
        )
        base.update(other)
        assert base.get_name() == "overlay"
        assert base.get_required() is False
        assert base.get_remap_dict() == {"a": "1", "b": "2"}
        assert base.get_env_dict() == {"X": "1", "Y": "2"}
        d = base.to_dict()
        assert d["build"] == "cmake"
        assert d["run"] == "./overlay"

    def test_empty_cmds_do_not_overwrite(self):
        base = NodeConfig(name="b", build_cmd="make", run_cmd="./run")
        overlay = NodeConfig(name="b")
        base.update(overlay)
        d = base.to_dict()
        assert d["build"] == "make"
        assert d["run"] == "./run"


class TestNodeConfigSerialization:

    def test_to_dict_minimal(self):
        nc = NodeConfig(name="n", run_cmd="cmd")
        d = nc.to_dict()
        assert d == {"name": "n", "run": "cmd", "required": True}
        assert "build" not in d
        assert "remap" not in d
        assert "env" not in d

    def test_to_dict_full(self):
        nc = NodeConfig(
            name="n",
            build_cmd="build",
            run_cmd="run",
            required=False,
            remap_dict={"a": "b"},
            env_dict={"K": "V"},
        )
        d = nc.to_dict()
        assert d["name"] == "n"
        assert d["build"] == "build"
        assert d["run"] == "run"
        assert d["required"] is False
        assert d["remap"] == {"a": "b"}
        assert d["env"] == {"K": "V"}

    def test_roundtrip(self):
        original = NodeConfig(
            name="rt",
            build_cmd="b",
            run_cmd="r",
            required=False,
            remap_dict={"x": "y"},
            env_dict={"E": "1"},
        )
        restored = NodeConfig.from_dict(original.to_dict())
        assert restored.to_dict() == original.to_dict()

    def test_from_dict_missing_optional(self):
        data = {"name": "n", "run": "r", "required": True}
        nc = NodeConfig.from_dict(data)
        assert nc.get_remap_dict() == {}
        assert nc.get_env_dict() == {}
        d = nc.to_dict()
        assert "build" not in d


# ───────────────────────── LaunchConfig ─────────────────────────


@pytest.fixture
def tmp_yml(tmp_path):
    """Return a helper that writes a dict as YAML and returns the path."""

    def _write(data: dict, name: str = "launch.yml") -> str:
        p = tmp_path / name
        with open(p, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return str(p)

    return _write


class TestLaunchConfigInit:

    def test_defaults(self):
        lc = LaunchConfig()
        assert lc.get_path() == "/tmp/hex_flow_launch.yml"
        assert lc.get_node_names() == []
        assert lc.get_node("missing") is None

    def test_log_to_file_requires_tui(self):
        lc = LaunchConfig(enable_tui=False, log_to_file=True)
        lc_tui = LaunchConfig(enable_tui=True, log_to_file=True)
        path_no_tui = self._export_and_load(lc)
        path_tui = self._export_and_load(lc_tui)
        assert path_no_tui["launcher"]["tui-log-to-file"] is False
        assert path_tui["launcher"]["tui-log-to-file"] is True

    @staticmethod
    def _export_and_load(lc: LaunchConfig) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
            lc_path = f.name
        try:
            lc_copy = LaunchConfig(
                local_only=False,
                enable_tui=lc._LaunchConfig__enable_tui,
                log_to_file=lc._LaunchConfig__log_to_file,
                save_path=lc_path,
            )
            lc_copy.export()
            with open(lc_path) as f:
                return yaml.safe_load(f)
        finally:
            os.unlink(lc_path)


class TestLaunchConfigNodes:

    def test_set_and_get_node(self):
        lc = LaunchConfig()
        nc = NodeConfig(run_cmd="run")
        lc.set_node("a", nc)
        assert lc.get_node("a") is nc
        assert nc.get_name() == "a"

    def test_set_node_syncs_name(self):
        nc = NodeConfig(name="old_name", run_cmd="r")
        lc = LaunchConfig()
        lc.set_node("new_name", nc)
        assert nc.get_name() == "new_name"

    def test_set_node_update_merges(self):
        lc = LaunchConfig()
        lc.set_node("x", NodeConfig(run_cmd="r1", env_dict={"A": "1"}))
        lc.set_node("x", NodeConfig(env_dict={"B": "2"}), update=True)
        node = lc.get_node("x")
        assert node.get_env_dict() == {"A": "1", "B": "2"}
        assert node.to_dict()["run"] == "r1"

    def test_set_nodes_replace(self):
        lc = LaunchConfig()
        lc.set_node("old", NodeConfig(run_cmd="r"))
        new_map = {"new": NodeConfig(name="new", run_cmd="r2")}
        lc.set_nodes(new_map)
        assert lc.get_node_names() == ["new"]

    def test_set_nodes_update(self):
        lc = LaunchConfig()
        lc.set_node("a", NodeConfig(run_cmd="r"))
        lc.set_nodes({"b": NodeConfig(name="b", run_cmd="r2")}, update=True)
        assert sorted(lc.get_node_names()) == ["a", "b"]


class TestLaunchConfigMerge:

    def test_merge_combines_nodes(self):
        lc1 = LaunchConfig()
        lc1.set_node("a", NodeConfig(run_cmd="r1"))
        lc2 = LaunchConfig()
        lc2.set_node("b", NodeConfig(run_cmd="r2"))
        lc1.merge(lc2)
        assert sorted(lc1.get_node_names()) == ["a", "b"]

    def test_merge_flags(self):
        lc1 = LaunchConfig(local_only=True, enable_tui=False, log_to_file=False)
        lc2 = LaunchConfig(local_only=False, enable_tui=True, log_to_file=False)
        lc1.merge(lc2)
        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
            path = f.name
        try:
            lc1._LaunchConfig__save_path = path
            lc1.export()
            with open(path) as f:
                data = yaml.safe_load(f)
            assert "router" not in data
            assert data["launcher"]["disable-tui"] is False
        finally:
            os.unlink(path)


class TestLaunchConfigExportImport:

    def _roundtrip(self, **kwargs) -> LaunchConfig:
        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as f:
            path = f.name
        try:
            lc = LaunchConfig(save_path=path, **kwargs)
            lc.set_node(
                "n1",
                NodeConfig(
                    run_cmd="./run",
                    build_cmd="make",
                    required=False,
                    remap_dict={"a": "b"},
                    env_dict={"K": "V"},
                ),
            )
            lc.export()
            return LaunchConfig.from_yml(path)
        finally:
            os.unlink(path)

    def test_roundtrip_local(self):
        lc = self._roundtrip(local_only=True, enable_tui=True, log_to_file=True)
        node = lc.get_node("n1")
        assert node is not None
        assert node.get_name() == "n1"
        assert node.get_required() is False
        assert node.get_remap_dict() == {"a": "b"}
        assert node.get_env_dict() == {"K": "V"}

    def test_roundtrip_non_local(self):
        lc = self._roundtrip(local_only=False, enable_tui=False, log_to_file=False)
        assert lc.get_node("n1") is not None

    def test_from_yml_no_router_key(self, tmp_yml):
        data = {
            "launcher": {"disable-tui": True, "tui-log-to-file": False},
            "nodes": [{"name": "a", "run": "r", "required": True}],
        }
        path = tmp_yml(data)
        lc = LaunchConfig.from_yml(path)
        assert lc.get_node("a") is not None

    def test_from_yml_no_nodes_key(self, tmp_yml):
        data = {"launcher": {"disable-tui": True, "tui-log-to-file": False}}
        path = tmp_yml(data)
        lc = LaunchConfig.from_yml(path)
        assert lc.get_node_names() == []

    def test_from_yml_empty_file(self, tmp_yml):
        path = tmp_yml({})
        lc = LaunchConfig.from_yml(path)
        assert lc.get_node_names() == []

    def test_from_yml_custom_save_path(self, tmp_yml):
        data = {"launcher": {"disable-tui": False, "tui-log-to-file": False}}
        path = tmp_yml(data)
        lc = LaunchConfig.from_yml(path, save_path="/tmp/custom.yml")
        assert lc.get_path() == "/tmp/custom.yml"

    def test_export_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            deep = os.path.join(td, "a", "b", "c", "out.yml")
            lc = LaunchConfig(save_path=deep)
            lc.export()
            assert os.path.isfile(deep)
