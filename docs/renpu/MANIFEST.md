# 仁谱 Renpu · 发布清单 v0.3

工作用到 · 别人拿到即用 · 不漏东西

## 完整性自检（你可以打开 `tests/test_smoke.py` 跑一遍）

| 项 | 文件 / 状态 |
|---|---|
| 1. plugin 元数据 | `plugin.json` ✅ |
| 2. skill 入口（agent 看） | `SKILL.md` ✅ |
| 3. 主文档（人读） | `README.md` ✅ |
| 4. 安装指引 | `INSTALL.md` ✅ |
| 5. 5 分钟上手 | `QUICKSTART.md` ✅ |
| 6. 排障表 | `TROUBLESHOOT.md` ✅ |
| 7. 视频脚本 | `docs/VIDEO_SCRIPT.md` ✅ |
| 8. CLI 入口（Unix） | `bin/renpu` ✅ |
| 9. CLI 入口（Windows） | `bin/renpu.cmd` ✅ |
| 10. 一键安装（Unix） | `scripts/install.sh` ✅ |
| 11. 一键安装（Windows） | `scripts/install.ps1` ✅ |
| 12. 端到端冒烟 | `tests/test_smoke.py` ✅ ALL GREEN |

## 代码

| 文件 | 说明 |
|---|---|
| `cli.py` | 命令行入口（renpu who / search / ingest ...） |
| `server.py` | 本地 HTTP API（127.0.0.1 only） |
| `core.py` | 六域存储（person / identity / tag / room / conversation / msg / event / edge / todo） |
| `config.py` | 三层回退配置（env > ~/.config/renpu/config.json > defaults） |
| `schema.sql` | SQLite schema |
| `adapters/wechat.py` | 微信 4.x 摄取 |
| `adapters/_wechat_decrypt.py` | 微信 4.x 解密（仁谱 自带，不依赖外部脚本） |
| `adapters/demo.py` | 零配置演示数据（让任何用户先跑起来） |

## 三个配置面

```
优先级：环境变量 > 用户 config > built-in 默认

Windows: %LOCALAPPDATA%\renpu\config.json
macOS:   ~/Library/Application Support/renpu/config.json
Linux:   ~/.config/renpu/config.json
```

常用配置键：`wc_live` / `wc_export` / `self_wxid` / `data_home` / `port` / `default_days`。

## 校验

跑这三条确认发布品正常：
```bash
renpu doctor                  # 环境体检
renpu init && renpu ingest --demo    # 零配置端到端
python tests/test_smoke.py  # 单元+冒烟（应 ALL GREEN）
```
