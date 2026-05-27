# XingShu BCI Developer Docs

欢迎使用 XingShu BCI Platform 的本地开发者接口。桌面应用会在本机启动一个仅监听 `127.0.0.1` 的 HTTP + WebSocket 服务，外部程序可以通过它读取 EEG 状态、订阅实时样本、控制采集、写入 marker、读取专注度分析结果，或把数据转发到自己的实验/交互系统。

这些文档面向接入方、研究工具开发者、教学实验开发者和第三方应用开发者。

## 你可以做什么

- 读取当前设备、采样率、通道数、滤波和分析配置。
- 连接设备或 synthetic board，并暂停、恢复、断开采集。
- 订阅实时样本、状态、分析结果和日志事件。
- 开始录制、插入实验 marker、停止录制。
- 读取专注度、放松度、频段功率和信号质量结果。
- 管理本机 API Token，或将数据输出给外部程序。

## 5 分钟接入

1. 打开 XingShu BCI 桌面应用。
2. 点击标题栏里的 **开发者中心**。
3. 创建一个 Token。
   - 只读实时数据：选择 `data` + `stream`。
   - 需要连接设备、录制、写 marker：再加 `control`。
4. 安装 Python SDK：

```bash
pip install xingshu-bci
```

本地源码开发时：

```bash
pip install -e ./sdk/python
```

5. 运行最小示例：

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto(token="xs_live_...") as client:
    print(client.version())
    print(client.status())
```

也可以通过环境变量传 Token：

```bash
export XINGSHU_BCI_TOKEN=xs_live_xxxx
```

```python
from xingshu_bci import XingShuClient

with XingShuClient.auto() as client:
    print(client.status().state)
```

## 文档入口

| 文档 | 适合谁 | 内容 |
|------|--------|------|
| [SDK.md](./SDK.md) | Python 开发者 | 安装、自动发现、实时样本、录制 marker、专注度控制。 |
| [API.md](./API.md) | 直接调用 REST/WebSocket 的开发者 | 鉴权、端点、事件、错误码、curl 示例。 |
| [OPENAPI.yaml](./OPENAPI.yaml) | 工具/代码生成用户 | OpenAPI 3.1 机器可读规格。 |
| [examples/](./examples) | 想直接跑示例的开发者 | Python、TypeScript、curl 示例。 |

## 本地 API 地址如何发现

API 端口是动态分配的。应用启动后会写入 bootstrap 文件：

```text
Windows: %APPDATA%\XingShu BCI\api\bootstrap.json
macOS:   ~/Library/Application Support/XingShu BCI/api/bootstrap.json
Linux:   ~/.config/XingShu BCI/api/bootstrap.json
```

Python SDK 的 `XingShuClient.auto()` 会自动读取这个文件。直接使用 REST/WebSocket 时，也可以从这个文件读取 `baseUrl` 和 `wsUrl`。

Token 不会写入 bootstrap 文件，需要用户在开发者中心创建后传给你的程序。

## 安全边界

- 服务只绑定 `127.0.0.1`，不会主动暴露到局域网。
- 所有 `/v1/*` 接口都需要 Token。
- Token 明文只在创建时显示一次，后续只保存哈希。
- 不要把 Token 写进仓库、实验日志或截图里。

## 兼容性

当前 API 版本为 `v1`，协议标识为 `xingshu-bci-api/1`。同一版本内字段会尽量只增不删；新增枚举值时，客户端应忽略未知值。
