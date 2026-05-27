# Local API Reference

XingShu BCI Platform 桌面应用提供一个本机 HTTP + WebSocket API。你可以用它把 XingShu BCI 接入自己的实验程序、交互应用、数据采集脚本或教学演示。

本文档面向直接调用 REST/WebSocket 的开发者。如果你使用 Python，建议优先阅读 [SDK.md](./SDK.md)。

## 基本信息

| 项目 | 说明 |
|------|------|
| 协议 | REST/JSON + WebSocket |
| 版本 | `/v1` |
| 监听地址 | `127.0.0.1` |
| 端口 | 动态分配 |
| 鉴权 | `Authorization: Bearer xs_live_...` |
| WebSocket 鉴权 | `Authorization` header 或 `?token=xs_live_...` |
| OpenAPI | [OPENAPI.yaml](./OPENAPI.yaml) |

API 地址由桌面应用写入 bootstrap 文件：

```text
Windows: %APPDATA%\XingShu BCI\api\bootstrap.json
macOS:   ~/Library/Application Support/XingShu BCI/api/bootstrap.json
Linux:   ~/.config/XingShu BCI/api/bootstrap.json
```

示例内容：

```json
{
  "baseUrl": "http://127.0.0.1:54321",
  "wsUrl": "ws://127.0.0.1:54321/v1/events",
  "apiVersion": "1.0.0",
  "protocol": "xingshu-bci-api/1",
  "running": true
}
```

## 获取 Token

1. 打开 XingShu BCI 桌面应用。
2. 点击标题栏 **开发者中心**。
3. 创建 Token，并选择需要的权限范围。
4. 复制 Token。明文只显示一次。

推荐权限：

| 场景 | Scopes |
|------|--------|
| 只读取状态和分析快照 | `data` |
| 订阅实时事件 | `stream` |
| 连接设备、控制采集、录制、写 marker | `control` |
| 管理 Token | `admin` |

`admin` 包含所有权限。`read_only` 是只读标记，建议普通外部应用优先使用 `data` + `stream`。

## 第一个请求

```bash
BASE=http://127.0.0.1:54321
TOKEN=xs_live_xxxx

curl -H "Authorization: Bearer $TOKEN" "$BASE/v1/version"
curl -H "Authorization: Bearer $TOKEN" "$BASE/v1/status"
```

连接 synthetic board：

```bash
curl -X POST "$BASE/v1/device/connect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"board":"synthetic","transport":"synthetic"}'
```

插入 marker：

```bash
curl -X POST "$BASE/v1/recording/markers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value":1,"label":"trial_start"}'
```

## 端点速查

### System

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/healthz` | 无 | 进程是否存活。 |
| GET | `/readyz` | 无 | 控制层是否就绪。 |
| GET | `/v1/version` | `data` | 应用、API、BrainFlow 版本。 |
| GET | `/v1/status` | `data` | 当前设备、采集、配置状态。 |

### Device

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/ports/serial` | `control` | 列出串口。 |
| POST | `/v1/device/connect` | `control` | 连接设备或 synthetic board。 |
| POST | `/v1/device/pause` | `control` | 暂停采集流。 |
| POST | `/v1/device/resume` | `control` | 恢复采集流。 |
| POST | `/v1/device/disconnect` | `control` | 断开当前设备。 |

`/v1/device/connect` 请求体示例：

```json
{
  "board": "synthetic",
  "transport": "synthetic"
}
```

串口设备示例：

```json
{
  "board": "cyton",
  "transport": "serial",
  "serialPort": "COM3"
}
```

Wi-Fi 设备示例：

```json
{
  "board": "cyton_wifi",
  "transport": "wifi",
  "ipAddress": "192.168.4.1",
  "ipPort": 6987
}
```

### Config

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/config/filter` | `data` | 读取滤波配置。 |
| POST | `/v1/config/filter` | `control` | 更新滤波配置。 |
| GET | `/v1/config/analysis` | `data` | 读取分析配置。 |
| POST | `/v1/config/analysis` | `control` | 更新分析配置。 |

### Recording

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/recording/status` | `data` | 录制、导出、回放状态。 |
| POST | `/v1/recording/start` | `control` | 开始录制。 |
| POST | `/v1/recording/pause` | `control` | 暂停录制。 |
| POST | `/v1/recording/resume` | `control` | 恢复录制。 |
| POST | `/v1/recording/stop` | `control` | 停止录制。 |
| POST | `/v1/recording/markers` | `control` | 插入事件 marker。 |

Marker 请求体：

```json
{
  "value": 2,
  "label": "stimulus_on"
}
```

### Playback

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| POST | `/v1/playback/open` | `control` | 通过文件对话框打开回放会话。 |
| POST | `/v1/playback/start` | `control` | 开始或继续回放。 |
| POST | `/v1/playback/pause` | `control` | 暂停回放。 |
| POST | `/v1/playback/seek` | `control` | 跳转到样本位置。 |
| POST | `/v1/playback/stop` | `control` | 停止回放。 |
| POST | `/v1/playback/export/bdf` | `control` | 导出 BDF+ 文件。 |

### Signal Quality

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/signal-quality/latest` | `data` | 读取最新信号质量结果。 |
| POST | `/v1/signal-quality/start` | `control` | 开始信号质量检测。 |
| POST | `/v1/signal-quality/stop` | `control` | 停止信号质量检测。 |

### Analysis

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/analysis/latest` | `data` | 最新完整分析快照。 |
| GET | `/v1/analysis/focus/latest` | `data` | 专注度/放松度快照。 |
| GET | `/v1/analysis/bands/latest` | `data` | 频段功率快照。 |

### Networking

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/networking/config` | `data` | 读取网络输出配置。 |
| POST | `/v1/networking/config` | `control` | 更新网络输出配置。 |
| GET | `/v1/networking/status` | `data` | 读取网络输出状态。 |
| POST | `/v1/networking/start` | `control` | 开始网络输出。 |
| POST | `/v1/networking/stop` | `control` | 停止网络输出。 |

### Logs

| Method | Path | Scope | 用途 |
|--------|------|-------|------|
| GET | `/v1/logs?limit=200` | `data` | 最近的应用日志。最大 `500`。 |

### Token Management

这些接口需要 `admin` scope。普通第三方应用通常不需要调用。

| Method | Path | 用途 |
|--------|------|------|
| GET | `/v1/auth/tokens` | 列出现有 Token 元数据。 |
| POST | `/v1/auth/tokens` | 创建 Token。 |
| POST | `/v1/auth/tokens/revoke` | 撤销 Token。 |

创建 Token：

```json
{
  "name": "experiment-script",
  "scopes": ["data", "stream", "control"],
  "expiresInDays": 30
}
```

响应里的 `token` 明文只返回一次。

## WebSocket 实时事件

连接地址来自 bootstrap 文件的 `wsUrl`：

```text
ws://127.0.0.1:<port>/v1/events?token=xs_live_...&events=samples,analysis,status
```

`events` 参数可省略，省略时订阅全部事件。每帧都是 JSON：

```json
{
  "type": "samples",
  "seq": 1234,
  "timestampMs": 1722000000123,
  "payload": {}
}
```

连接成功后，服务端会先发送一帧 `status`，随后按事件类型推送数据。

常见事件：

| type | 说明 |
|------|------|
| `samples` | 实时样本块。 |
| `analysis` | FFT、频段功率、专注度等分析快照。 |
| `status` | 设备或采集状态变化。 |
| `recording.status` | 录制/导出状态变化。 |
| `recording.marker` | 新插入 marker。 |
| `signalQuality` | 信号质量快照。 |
| `networking.status` | 网络输出状态变化。 |
| `log` | 应用日志。 |
| `heartbeat` | 服务端心跳。 |

## 响应与错误

成功响应根据端点返回对象。控制类操作通常包含：

```json
{
  "ok": true,
  "requestId": "req_xxxxxxxx"
}
```

错误响应：

```json
{
  "ok": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Token 权限不足，需要 scope: control"
  },
  "requestId": "req_xxxxxxxx"
}
```

常见错误：

| HTTP | code | 说明 |
|------|------|------|
| 400 | `BAD_REQUEST` | JSON 无效、请求体过大或参数缺失。 |
| 401 | `UNAUTHORIZED` | Token 缺失、错误或过期。 |
| 403 | `FORBIDDEN` | Token 权限不足。 |
| 404 | `NOT_FOUND` | 路由不存在。 |
| 500 | `INTERNAL_ERROR` | 应用内部错误。 |

## 兼容性建议

- 使用 `GET /v1/version` 检查 `apiVersion` 和 `protocol`。
- 客户端应忽略未知字段。
- 新增枚举值时，客户端应保留默认分支。
- 破坏性变更会进入新的路径版本，例如 `/v2`。
