<h1 align="center">HEX FLOW CORE</h1>

<p align="center">
    <a href="https://github.com/hexfellow/hex_flow_core/stargazers">
        <img src="https://img.shields.io/github/stars/hexfellow/hex_flow_core?style=flat-square&logo=github" />
    </a>
    <a href="https://github.com/hexfellow/hex_flow_core/forks">
        <img src="https://img.shields.io/github/forks/hexfellow/hex_flow_core?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/hexfellow/hex_flow_core/issues">
        <img src="https://img.shields.io/github/issues/hexfellow/hex_flow_core?style=flat-square&logo=github" />
    </a>
</p>

---

# 📖 Overview

## What is `hex_flow_core`

`hex_flow_core` is the Python core library for the HEXFELLOW **hex-flow** framework. It provides Zenoh-based publish/subscribe node abstractions and launch configuration utilities, enabling multi-node orchestration for HEXFELLOW robots, sensors, and simulators.

## What problem it solves

- **Pub/Sub communication**: Nodes publish and subscribe to topics over [Eclipse Zenoh](https://zenoh.io/), supporting high-throughput binary payloads (images, commands, sensor data).
- **Topic remapping**: Each node can remap logical topic names to actual Zenoh keys via environment variables, enabling flexible deployment without code changes.
- **Launch orchestration**: `LaunchConfig` and `NodeConfig` generate YAML launch files consumed by `hexflow run`, managing multiple nodes, build steps, environment variables, and router settings from a single Python script.

## Target users

- Engineers integrating HEXFELLOW robots into their systems.
- Researchers running experiments with HEXFELLOW robots.

# 📦 Installation

## Requirements

- **Python** >= 3.10
- **OS**: Ubuntu (tested on 22.04)
- **Core dependencies**:
  - `eclipse-zenoh` >= 1.9.0
  - `envlog` == 1.0.0
  - `hex_util_runtime` >= 0.0.0, < 0.1.0
  - `pyyaml` >= 6.0

## Install `hex-flow-cli`

For Ubuntu or any Debian-based system, install Zenoh and hex-flow CLI:

```bash
sudo apt update
sudo apt install -y curl gpg

curl -L https://download.eclipse.org/zenoh/debian-repo/zenoh-public-key | sudo gpg --dearmor --yes --output /etc/apt/keyrings/zenoh-public-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/zenoh-public-key.gpg] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list > /dev/null
sudo apt update
sudo apt install -y zenoh

curl -fsSL https://raw.githubusercontent.com/hexfellow/hex-flow/main/install.sh | sh
```

For other systems, please install `zenohd` yourself, then run the [install script](https://raw.githubusercontent.com/hexfellow/hex-flow/main/install.sh).

## Install `hex-flow-core` from PyPI

You can install `hex-flow-core` from PyPI:

```bash
uv pip install hex_flow_core
```

## Install `hex-flow-core` from source

We provide a [venv.sh](venv.sh) script to create a virtual environment with all dependencies installed. However, you need to install uv first. For uv installation, please refer to `uv` official [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

Then you can use our [venv.sh](venv.sh) to create a virtual environment with all dependencies installed:

```bash
git clone https://github.com/hexfellow/hex_flow_core.git
cd hex_flow_core
./venv.sh
```

# 📑 API

## `NodeCallback`

Low-level base class wrapping a Zenoh session with publisher/subscriber management, topic remapping, and structured logging.

```python
from hex_flow_core import NodeCallback

node = NodeCallback("my_node")
node.start()

node.create_pub("my/topic")
node.pub("my/topic", b"hello")

node.create_sub("other/topic", lambda sample: print(sample.payload.to_bytes()))

while node.is_working():
    time.sleep(1)

node.stop()
```

**Environment variables** read at init:

| Variable             | Description                                           | Default         |
| -------------------- | ----------------------------------------------------- | --------------- |
| `HEX_FLOW_NODE_NAME` | Overrides the `name` argument                         | constructor arg |
| `HEX_FLOW_REMAP`     | JSON dict mapping logical topics to actual Zenoh keys | `{}`            |
| `RUST_LOG`           | Log level passed to `envlog`                          | `"info"`        |

## `Node`

Higher-level subclass of `NodeCallback` that automatically buffers received messages in bounded deques, providing a polling-style `get()` interface.

```python
from hex_flow_core import Node

node = Node("my_node")
node.start()

node.create_sub("sensor/data", maxlen=20)

data = node.get("sensor/data", latest=True)
if data is not None:
    print(f"received {len(data)} bytes")

node.stop()
```

## `NodeConfig`

Describes a single node for launch: name, build/run commands, required flag, topic remaps, and environment variables.

```python
from hex_flow_core import NodeConfig

cfg = NodeConfig(
    name="cam_publisher",
    run_cmd="python cam_pub.py",
    build_cmd="pip install -e .",
    required=True,
    remap_dict={"camera/rgb": "robot_a/camera/rgb"},
    env_dict={"RUST_LOG": "debug"},
)
```

## `LaunchConfig`

Aggregates multiple `NodeConfig` entries and exports a YAML launch file for `hexflow run`.

```python
from hex_flow_core import LaunchConfig, NodeConfig

launch = LaunchConfig(
    local_only=True,
    enable_tui=False,
    log_to_file=True,
    save_path="/tmp/my.launch.yml",
)

launch.set_node("cam", NodeConfig(run_cmd="python cam.py"))
launch.set_node("ctrl", NodeConfig(run_cmd="python ctrl.py"))

path = launch.export()
print(path)  # /tmp/my.launch.yml
```

The exported YAML can be used with:

```bash
hexflow run /tmp/my.launch.yml
```

# 💡 Example

**Examples are only available for users who install `hex-flow-core` from source code**. Follow the steps below to run the examples:

```bash
git clone https://github.com/hexfellow/hex_flow_core.git
cd hex_flow_core

./venv.sh
source .venv/bin/activate

hexflow run examples/test.launch.py
```

This launches 8 command publishers (~1000 Hz each), 6 image publishers (~50 Hz each), and 1 subscriber that validates payloads and logs throughput.

> **Note**: Examples require `numpy` (`pip install numpy`).

# 📄 License

Apache License 2.0. See [LICENSE](LICENSE).

# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hexfellow/hex_flow_core&type=Date)](https://star-history.com/#hexfellow/hex_flow_core&Date)

# 👥 Contributors

<a href="https://github.com/hexfellow/hex_flow_core/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=hexfellow/hex_flow_core" />
</a>
