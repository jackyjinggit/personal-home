# INSTALL · 接真微信库

> 默认 demo 数据够体验。要接你真微信数据库这一步必须做。

## 0 · 前置

- Windows 微信 4.x 客户端（macOS / Linux 也行，但路径不同）
- 曾经在微信 PC 端登录过（否则 DB 没东西可读）
- 与本机：同一台机器、同一用户

## 1 · 拿到微信 live 库路径

微信把 local db 存在 `<Documents>/Tencent Files/xwechat_files/<wxid_xxx>/db_storage/`。

**Windows 常见位置**：
- `C:\Users\<你的 Windows 用户名>\Documents\Tencent Files\xwechat_files\<你的 wxid>\db_storage\`
- `D:\Users\<你的 Windows 用户名>\Documents\Tencent Files\xwechat_files\<你的 wxid>\db_storage\`

**macOS**：
- `~/Documents/Tencent Files/xwechat_files/<wxid>/db_storage/`

**Linux**：
- 微信 Linux 版（如果有）通常类似 `~/Documents/Tencent Files/...`

> 不知道 wxid？让 `renpu doctor` 自动探测（如果它在 `Documents/Tencent Files/xwechat_files/*/db_storage` 找到了就会显示）。否则去 `wxid_*` 文件夹名里看一长串数字+字母就是。

## 2 · 拿到解密密钥（`db_key.txt`）

微信 PC 端会自动写一份解密密钥到自己的目录下。位置：

```
<你的 wc_live>/db_key.txt
```

如果文件存在 → 复制或记下路径（仁谱 会自己找）：
- Windows：`D:\Users\...\Documents\Tencent Files\xwechat_files\<wxid>\db_key.txt`
- Linux/macOS：类似位置

如果文件不存在 → 看微信客户端里搜「备份与恢复」，或者启动一次微信让它写。

> **实测补充（2026-10-26）**：微信**不保证**把 `db_key.txt` 放在 `wc_live` 旁边。
> 如果那里没有，但你有自己的解密工具链（一个含 `fresh_pull.py` 的目录），
> **密钥通常就在那个目录的根下** —— 仁谱 会从 `wc_export` 里读它。
> 两个都找不到时，`renpu doctor` 会明确告诉你缺哪一步。

## 3 · 配置 仁谱

**方式 A · 写配置文件**（推荐，跨进程生效）

Windows 编辑 `%LOCALAPPDATA%\renpu\config.json`：
```json
{
  "wc_live": "D:\\Users\\你的用户名\\Documents\\Tencent Files\\xwechat_files\\你的wxid\\db_storage",
  "self_wxid": "wxid_xxxxxxxx"
}
```

macOS：`~/Library/Application Support/renpu/config.json`  
Linux：`~/.config/renpu/config.json`

**方式 B · 环境变量**（一次性）
```bash
# Windows PowerShell
$env:RENPU_WC_LIVE   = "D:\Users\...\db_storage"
$env:RENPU_SELF_WXID = "wxid_xxxxxxxx"

# macOS/Linux
export RENPU_WC_LIVE="/Users/you/Documents/Tencent Files/.../db_storage"
export RENPU_SELF_WXID="wxid_xxxxxxxx"
```

> `self_wxid` 通常可以省 — 让 `renpu doctor` 自动猜（取 contact 表里第一个完整 wxid）。
> 不要把 `db_key.txt` 内容写进 config.json —— 它是磁盘文件，仁谱 会自动读。

## 4 · 体检

```bash
renpu doctor
```
应看见：
```
WC_LIVE .................. D:\Users\...\db_storage     ✅ 配置
SELF_WXID ................ wxid_xxxxxxx                ✅ 自动探测成功
db_key.txt ................ ✅ 找到
```

不 OK 的话看 [TROUBLESHOOT.md](TROUBLESHOOT.md) 的「微信库读不到」节。

## 5 · 摄取

```bash
renpu ingest --pull          # 自动解密 + 灌库，约 30-90 秒
renpu stats                 # 看看灌进去多少人/消息
```

## 6 · 试一下

```bash
renpu who <你常用联系人名>
```
或：
```bash
renpu search "你们之前的关键词"
```

## 进阶

### 改默认摄取窗口（默认近 90 天）
```bash
renpu ingest --days 30
```
或配置：`{"default_days": 30}`。

### 改默认端口 / 数据路径
```bash
renpu serve --port 9001         # 临时
export RENPU_PORT=9001          # 持久
export RENPU_DATA_HOME=~/vault/renpu
```

### 接蒋平版 `wc_export`（高级）
如果你已经用蒋平版的 `wc_export/fresh_pull.py`：
```json
{
  "wc_export": "~/my/wechat-export",
  "wc_live": null
}
```
仁谱 会优先用你已有的脚本（不重复造轮子）；`wc_live` 可省。

> **实测补充（2026-10-26）**：`wc_export` 里的 `fresh_pull.py` 常常**硬编码**了
> 微信 live 库路径。搬机器或换盘符后它会指向旧位置 —— 那时改 `wc_export`
> 里的那个路径，或直接在 `config.json` 里同时配 `wc_live`（仁谱 的内置
> 解密器会用 `wc_live`）。
>
> 端到端实测跑通的一次配置：
> ```json
> {
>   "wc_live": "D:/.../Tencent Files/xwechat_files/<wxid>/db_storage",
>   "wc_export": "F:/.../wc_export",
>   "self_wxid": "wxid_xxxxxxxxx"
> }
> ```
> `self_wxid` 是你自己的 wxid：填了之后，「我」在档案里显示成你的昵称，
> 不填会退化成 `me`。

### 完全本地、可重入
`renpu ingest --pull` 任何时候可重跑——幂等已保证（重复 sync 不会膨胀）。

### 摄取会遮蔽什么
消息摘要入库前会自动遮蔽敏感标识（实测 20 万条真实消息，残留 0）：

| 类型 | 处理 |
|---|---|
| 手机号 | `[手机号]` |
| 身份证 / 卡号 | `[身份证]` `[卡号]` |
| 微信 id / 公众号 id | `[微信id]` `[公众号id]` |
| 邮箱 | `[邮箱]` |
| QQ 号 / 微信号 | `[QQ号]` `[微信号]` |

> 注意：微信的 `@某人` 提及**不是**邮箱，**不会被遮** —— 那是给人看的名字，
> 不是账号。