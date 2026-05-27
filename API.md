# XingShu BCI Platform — Local API Reference (v1)

> 本文档描述星枢 BCI 平台桌面应用对外暴露的本地 HTTP + WebSocket API（`v1`）。
> 设计文档见 [`API_DESIGN.md`](./API_DESIGN.md)，机器可读规格见 [`OPENAPI.yaml`](./OPENAPI.yaml)。

## 1. 概览

- **绑定地址**：仅监听 `127.0.0.1`，端口在每次启动随机选取。
- **发现方式**：写入 `%APPDATA%\XingShu BCI\api\bootstrap.json`，SDK 自动读取。
- **协议**：REST/JSON + WebSocket。
- **鉴权**：`Authorization: Bearer xs_live_<hex>` 或 `?token=<...>`。
- **CORS**：允许任意来源，仅本机访问。
- **错误格式**：

```json
{
  "ok": false,
  "error": { "code": "FORBIDDEN", "message": "Token 权限不足，需要 scope: control" },
  "requestId": "req_xxxxxxxx"
}
```

## 2. 启动 / 停止

API 服务随应用启动自动运行。在「开发者中心」中可手动启动/停止。

```text
http://127.0.0.1:<port>      REST
ws://127.0.0.1:<port>/v1/events  WebSocket
```

## 3. Token 与 Scopes

| Scope | 含义 |
|-------|------|
| `admin` | 管理（含 Token 列表/创建/撤销）。 |
| `control` | 设备连接、采集、记录、播放、信号检测、网络转发等控制类操作。 |
| `data` | 读取状态、配置、快照与日志。 |
| `stream` | WebSocket 订阅实时事件。 |
| `read_only` | 仅限 `data` + `stream` 子集的只读访问。 |

Token 通过 SHA-256 哈希持久化到 `%APPDATA%\XingShu BCI\api\tokens.json`，**明文仅在创建时返回一次**。

## 4. 端点速查

完整列表见 [`OPENAPI.yaml`](./OPENAPI.yaml)。主要端点：

### System
- `GET  /healthz` · `GET /readyz`（无鉴权）
- `GET  /v1/version` · `GET /v1/status`

### Device
- `GET  /v1/ports/serial`
- `POST /v1/device/connect`
- `POST /v1/device/pause` · `/resume` · `/disconnect`

### Config
- `GET/POST /v1/config/filter`
- `GET/POST /v1/config/analysis`

### Recording
- `GET  /v1/recording/status`
- `POST /v1/recording/start` · `/pause` · `/resume` · `/stop`
- `POST /v1/recording/markers`

### Playback
- `POST /v1/playback/open` · `/start` · `/pause` · `/seek` · `/stop`
- `POST /v1/playback/export/bdf`

### Signal Quality
- `GET  /v1/signal-quality/latest`
- `POST /v1/signal-quality/start` · `/stop`

### Networking
- `GET/POST /v1/networking/config`
- `GET  /v1/networking/status`
- `POST /v1/networking/start` · `/stop`

### Analysis
- `GET  /v1/analysis/latest`
- `GET  /v1/analysis/focus/latest`
- `GET  /v1/analysis/bands/latest`

### Logs
- `GET  /v1/logs?limit=200`

### Auth
- `GET  /v1/auth/tokens`
- `POST /v1/auth/tokens`
- `POST /v1/auth/tokens/revoke`

## 5. WebSocket 事件

```
GET /v1/events?token=xs_live_...&events=samples,analysis,status
Upgrade: websocket
```

`events` 参数可省略（订阅全部）。每帧 JSON：

```json
{
  "type": "samples",
  "seq": 1234,
  "timestampMs": 1722000000123,
  "payload": { "...": "..." }
}
```

事件类型：
- `samples` —— 实时样本块。
- `analysis` —— 滤波后 FFT/带能/专注度等综合快照。
- `status` —— 设备/采集状态变化。
- `recording.status` —— 录制/导出状态。
- `recording.marker` —— 新插入的事件标记。
- `signalQuality` —— 信号质量快照。
- `networking.status` —— 网络转发状态。
- `log` —— 应用日志。
- `heartbeat` —— 服务端 30s 心跳。

## 6. 常见错误码

| HTTP | code | 说明 |
|------|------|------|
| 400 | `BAD_REQUEST` | 请求体无效或缺少字段。 |
| 401 | `UNAUTHORIZED` | Token 缺失/失效。 |
| 403 | `FORBIDDEN` | 权限不足。 |
| 404 | `NOT_FOUND` | 路由不存在。 |
| 500 | `INTERNAL_ERROR` | 服务端异常。 |

## 7. 示例

最小 curl：
```bash
TOKEN=xs_live_xxxx
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:PORT/v1/status
```

完整示例见 [`examples/`](./examples) 与 SDK 文档 [`SDK.md`](./SDK.md)。

## 8. 兼容性策略

- 字段**只增不删**，破坏性变更将 bump 到 `/v2/`。
- 新增枚举值客户端应忽略未知值。
- `apiVersion`、`protocol` 字段可用于运行时探测。

## 9. 安全

- API 仅监听 `127.0.0.1`，不会暴露到局域网。
- Token 单向哈希存储，明文仅在创建时返回一次。
- 客户端不应将 Token 提交到代码仓库或共享日志。
