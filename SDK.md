# XingShu BCI Platform — Developer SDK

> 本文档介绍官方维护的开发者 SDK。当前提供 Python SDK（`xingshu-bci`），TypeScript SDK 计划中。

## Python SDK

源码位于 [`sdk/python/`](../sdk/python)。

### 安装

```bash
# 本地安装（开发时）
pip install -e ./sdk/python
# 或从 PyPI（计划发布后）
pip install xingshu-bci
```

依赖：`httpx>=0.27`、`websocket-client>=1.7`。

### 快速开始

```python
from xingshu_bci import XingShuClient

# 自动发现本地 API，然后通过参数或环境变量提供 Token
client = XingShuClient.auto(token="xs_live_...")

# 或显式构造
# client = XingShuClient(base_url="http://127.0.0.1:54321", token="xs_live_...")

print(client.version())
print(client.status())
```

如果你更喜欢命令行示例，仓库里的 [`docs/examples`](../docs/examples) 也可以直接拿来参考：

- `python/live_samples.py`：WebSocket 实时样本订阅
- `python/recording_markers.py`：录制、打 marker、停止录制
- `python/focus_control.py`：读取专注力 / 放松度快照
- `curl/status.sh`：快速查看服务状态

### 设备 / 录制

```python
client.connect(board="synthetic", transport="synthetic")
client.start_recording()
client.insert_marker(value=1, label="trial_start")
import time; time.sleep(2)
client.stop_recording()
client.disconnect()
```

### 实时事件（WebSocket）

```python
for event in client.events(types=["samples", "analysis"]):
    if event.type == "samples":
        first_sample = event.payload["data"][0]
        print("samples:", first_sample)
    elif event.type == "analysis":
        print("focus:", event.payload.get("focus"))
```

`events()` 返回生成器，自动处理心跳、过滤事件类型。按 `Ctrl+C` 退出。

### 专注力 / 放松度高级流：`SmoothedFocusStream`

底层 API 推送的原始 `focus.prediction` 在阈值附近会有 ±0.05 量级的噪声，直接用于
控制 IoT 设备（灯泡、风扇、电机）会"哒哒"闪烁。`SmoothedFocusStream` 封装了
**EMA 平滑 + 滞回阈值 + 限速 + 死区映射**，让应用代码只关心动作本身：

```python
from xingshu_bci import XingShuClient, SmoothedFocusStream

with XingShuClient.auto() as client:
    if client.status().state == "idle":
        client.connect(board="synthetic", transport="synthetic")

    for upd in SmoothedFocusStream(client, metric="concentration"):
        # upd.raw       原始 prediction (0-1)
        # upd.smoothed  EMA 平滑后 (0-1)
        # upd.is_on     当前滞回状态 (bool)
        # upd.brightness 死区映射后的 0-100 输出
        # upd.rising / upd.falling 仅在状态翻转的那一帧为 True
        if upd.rising:
            print("→ ON")
        elif upd.falling:
            print("→ OFF")
        if upd.is_on:
            print(f"brightness {upd.brightness}%")
```

构造参数（全部带合理默认值，可单独覆盖）：

| 参数 | 默认 | 含义 |
|---|---|---|
| `metric` | `"concentration"` | 或 `"relaxation"`，会自动 push 到服务端 |
| `smoothing` | `0.25` | EMA α，越小越平滑越延迟 |
| `on_threshold` | `0.45` | 平滑值升至此触发 `rising` |
| `off_threshold` | `0.30` | 平滑值降至此触发 `falling`（滞回） |
| `dead_zone` | `0.20` | 低于此值映射为亮度 0 |
| `min_interval_s` | `0.2` | 两次 yield 最小间隔，限流 IoT |
| `auto_configure` | `True` | 进入循环前自动 `set_analysis_config` |

### 上下文管理器

```python
with XingShuClient.auto(token="xs_live_...") as c:
    c.start_signal_check(board="cyton", transport="serial", serialPort="COM3")
    snapshot = c.signal_quality_latest()
    print(snapshot)
    c.stop_signal_check()
```

### Token 管理（admin scope）

```python
new_token = client.create_token(name="my-script", scopes=["data", "stream"], expires_in_days=30)
print(new_token.token)  # 只显示一次

for tok in client.list_tokens():
    print(tok.id, tok.name, tok.scopes)

client.revoke_token(new_token.id)
```

### 错误处理

```python
from xingshu_bci import XingShuError, XingShuAuthError

try:
    client.start_recording()
except XingShuAuthError:
    print("Token 失效，请到开发者中心重新创建。")
except XingShuError as e:
    print("API 错误:", e.code, e.message)
```

### 高级：低层 HTTP 调用

```python
resp = client.request("POST", "/v1/recording/markers", json={"value": 2, "label": "stim_off"})
print(resp.json())
```

## TypeScript SDK（计划中）

提案 API：

```ts
import { XingShuClient } from "@xingshu-bci/sdk";

const client = await XingShuClient.auto();
await client.connect({ board: "synthetic", transport: "synthetic" });

for await (const ev of client.events(["samples"])) {
  console.log(ev.payload);
}
```

## 自动发现机制

SDK 通过读取以下文件自动获取地址与端口：

- Windows: `%APPDATA%\XingShu BCI\api\bootstrap.json`
- macOS:   `~/Library/Application Support/XingShu BCI/api/bootstrap.json`
- Linux:   `~/.config/XingShu BCI/api/bootstrap.json`（保留位置）

文件示例：

```json
{
  "baseUrl": "http://127.0.0.1:54321",
  "wsUrl":   "ws://127.0.0.1:54321/v1/events",
  "tokenFile": "...tokens.json",
  "apiVersion": "1.0.0",
  "appVersion": "0.4.3",
  "running": true,
  "updatedAt": "2026-05-26T06:00:00.000Z"
}
```

Token 永远不写入 bootstrap.json，需用户在「开发者中心」手动创建并复制。
