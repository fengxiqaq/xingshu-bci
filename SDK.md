# Python SDK Guide

`xingshu-bci` 是 XingShu BCI Platform 的官方 Python SDK。它会自动发现桌面应用启动的本地 API，并封装 REST 与 WebSocket 调用，适合实验脚本、交互原型、教学演示和第三方应用集成。

## 安装

从源码安装：

```bash
pip install -e ./sdk/python
```

发布到包仓库后：

```bash
pip install xingshu-bci
```

依赖：

- Python 3.9+
- `httpx>=0.27`
- `websocket-client>=1.7`

## 准备 Token

1. 打开 XingShu BCI 桌面应用。
2. 点击标题栏 **开发者中心**。
3. 创建 Token。
4. 复制 Token，并通过参数或环境变量传给 SDK。

```bash
export XINGSHU_BCI_TOKEN=xs_live_xxxx
```

普通只读程序建议使用 `data` + `stream`。需要连接设备、录制或插入 marker 时，再增加 `control`。

## 第一个脚本

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    version = client.version()
    status = client.status()
    print(version.apiVersion, version.protocol)
    print(status.state, status.board, status.sampleRate)
```

`XingShuClient.auto()` 会读取桌面应用写入的 bootstrap 文件，所以你不需要硬编码端口。

也可以显式传入地址：

```python
from xingshu_bci import XingShuClient

client = XingShuClient(
    base_url="http://127.0.0.1:54321",
    token="xs_live_...",
)
```

## 连接设备

Synthetic board 适合快速开发和调试：

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    if client.status().state == "idle":
        client.connect(board="synthetic", transport="synthetic")

    print(client.status())
```

串口设备示例：

```python
with XingShuClient.auto() as client:
    ports = client.list_serial_ports()
    print(ports)

    client.connect(
        board="cyton",
        transport="serial",
        serialPort="COM3",
    )
```

断开：

```python
client.disconnect()
```

## 订阅实时样本

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    if client.status().state == "idle":
        client.connect(board="synthetic", transport="synthetic")

    for event in client.events(types=["samples", "analysis", "status"]):
        if event.type == "samples":
            data = event.payload.get("data") or []
            if data and data[0]:
                print("ch0 first sample:", data[0][0])
        elif event.type == "analysis":
            print("focus:", event.payload.get("focus"))
        elif event.type == "status":
            print("state:", event.payload.get("state"))
```

`events()` 返回同步生成器。按 `Ctrl+C` 结束程序即可。

## 录制并插入 marker

```python
import time
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    client.connect(board="synthetic", transport="synthetic")
    try:
        client.start_recording()
        client.insert_marker(value=1, label="trial_start")
        time.sleep(2)
        client.insert_marker(value=2, label="stimulus_on")
        time.sleep(1)
        client.insert_marker(value=3, label="stimulus_off")
        print(client.stop_recording())
    finally:
        client.disconnect()
```

## 读取专注度 / 放松度

轮询最新快照：

```python
import time
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    if client.status().state == "idle":
        client.connect(board="synthetic", transport="synthetic")

    while True:
        snapshot = client.analysis_focus_latest()
        print(snapshot.get("focus"))
        time.sleep(0.5)
```

实时事件方式：

```python
for event in client.events(types=["analysis"]):
    focus = event.payload.get("focus") or {}
    if focus.get("state") == "ready":
        print(focus.get("prediction"))
```

## 用专注度控制外部设备

`SmoothedFocusStream` 封装了 EMA 平滑、滞回阈值、限速和亮度映射，适合把专注度/放松度接到灯泡、风扇、游戏或视觉刺激程序。

```python
from xingshu_bci import SmoothedFocusStream, XingShuClient

class Bulb:
    def on(self):
        print("[bulb] ON")

    def off(self):
        print("[bulb] OFF")

    def set_brightness(self, percent: int):
        print(f"[bulb] {percent}%")

with XingShuClient.auto() as client:
    if client.status().state == "idle":
        client.connect(board="synthetic", transport="synthetic")

    bulb = Bulb()
    for update in SmoothedFocusStream(client, metric="concentration"):
        if update.rising:
            bulb.on()
        elif update.falling:
            bulb.off()

        if update.is_on:
            bulb.set_brightness(update.brightness)
```

常用参数：

| 参数 | 默认 | 说明 |
|------|------|------|
| `metric` | `"concentration"` | 可选 `"concentration"` 或 `"relaxation"`。 |
| `smoothing` | `0.25` | EMA alpha，越小越平滑但延迟越高。 |
| `on_threshold` | `0.45` | 平滑值升至该阈值触发 `rising`。 |
| `off_threshold` | `0.30` | 平滑值降至该阈值触发 `falling`。 |
| `dead_zone` | `0.20` | 低于该值时亮度输出为 0。 |
| `min_interval_s` | `0.2` | 两次输出之间的最小间隔。 |
| `auto_configure` | `True` | 自动向服务端设置 focus metric。 |

## Token 管理

Token 管理接口需要 `admin` scope。

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    created = client.create_token(
        name="experiment-script",
        scopes=["data", "stream", "control"],
        expires_in_days=30,
    )
    print(created.token)  # 只显示一次

    for token in client.list_tokens():
        print(token.id, token.name, token.scopes)

    client.revoke_token(created.id)
```

## 错误处理

```python
from xingshu_bci import XingShuAuthError, XingShuForbiddenError, XingShuError

try:
    client.start_recording()
except XingShuAuthError:
    print("Token 缺失、错误或已过期。")
except XingShuForbiddenError:
    print("Token 权限不足，请在开发者中心创建带 control scope 的 Token。")
except XingShuError as exc:
    print(exc.status, exc.code, exc.message, exc.request_id)
```

## 低层 HTTP 调用

SDK 没封装到的端点可以直接调用：

```python
response = client.request(
    "POST",
    "/v1/recording/markers",
    json={"value": 9, "label": "custom_event"},
)
print(response.json())
```

## 常用方法索引

| 方法 | 说明 |
|------|------|
| `version()` | API 与应用版本。 |
| `status()` | 设备与采集状态。 |
| `list_serial_ports()` | 可用串口。 |
| `connect(...)` / `disconnect()` | 连接或断开设备。 |
| `pause()` / `resume()` | 暂停或恢复采集流。 |
| `events(types=[...])` | WebSocket 实时事件。 |
| `start_recording()` / `stop_recording()` | 录制控制。 |
| `insert_marker(value, label=...)` | 写入事件 marker。 |
| `analysis_focus_latest()` | 最新专注度/放松度快照。 |
| `signal_quality_latest()` | 最新信号质量结果。 |
| `logs(limit=200)` | 应用日志。 |

更多可运行示例见 [examples/](./examples)。
