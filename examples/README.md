# Runnable Examples

这些示例可以直接作为外部应用接入 XingShu BCI Platform 的起点。运行前请先打开桌面应用，并在 **开发者中心** 创建 Token。

## 准备环境

安装 Python SDK：

```bash
pip install -e ./sdk/python
```

或使用发布包：

```bash
pip install xingshu-bci
```

设置 Token：

```bash
export XINGSHU_BCI_TOKEN=xs_live_xxxx
```

Windows PowerShell：

```powershell
$env:XINGSHU_BCI_TOKEN = "xs_live_xxxx"
```

如果使用 curl 示例，还需要设置本地 API 地址：

```bash
export XINGSHU_BCI_BASE_URL=http://127.0.0.1:54321
```

`baseUrl` 可以在开发者中心或 bootstrap 文件中查看。

## 示例列表

| 文件 | 语言 | 需要 scopes | 用途 |
|------|------|-------------|------|
| [python/live_samples.py](./python/live_samples.py) | Python | `data`, `stream`, `control` | 连接 synthetic board，订阅实时样本、分析和状态事件。 |
| [python/recording_markers.py](./python/recording_markers.py) | Python | `data`, `control` | 录制短会话并插入实验 marker。 |
| [python/focus_control.py](./python/focus_control.py) | Python | `data`, `control` | 轮询专注度/放松度分析快照。 |
| [python/focus_lightbulb.py](./python/focus_lightbulb.py) | Python | `data`, `stream`, `control` | 用平滑后的专注度控制灯泡开关和亮度。 |
| [typescript/live_samples.ts](./typescript/live_samples.ts) | TypeScript | `data`, `stream` | Node.js WebSocket 实时订阅。 |
| [curl/status.sh](./curl/status.sh) | curl | `data` | 查询当前状态。 |

## 运行

Python 实时样本：

```bash
python docs/examples/python/live_samples.py
```

录制 marker：

```bash
python docs/examples/python/recording_markers.py
```

curl 状态查询：

```bash
./docs/examples/curl/status.sh
```

## 常见问题

**提示找不到本地 API**

确认桌面应用正在运行，并且开发者中心里 API 服务处于运行状态。

**提示缺少 Token**

设置 `XINGSHU_BCI_TOKEN`，或在代码里显式传入 `token="xs_live_..."`。

**提示权限不足**

示例需要的 scopes 在上表中列出。回到开发者中心创建一个带对应 scopes 的 Token。
