# TROUBLESHOOT · 排障

> 第一步：**跑 `renpu doctor`**。它会列出当前环境状态、缺什么、该做什么。

---

## 一、装不上 / 起不来

| 症状 | 原因 / 解法 |
|---|---|
| `renpu: command not found` | `bin/` 不在 PATH，或者直接 `python cli.py <cmd>` 临时用 |
| `ModuleNotFoundError: Crypto` | `pip install pycryptodome`（或在 venv 里 `source venv/bin/activate` 后再装） |
| `python: command not found` | 装 Python 3.10+（[python.org](https://python.org)；Windows 记得勾"Add to PATH"） |
| 双击 `bin\renpu.cmd` 后窗口闪退 | 在 cmd 里 `bin\renpu.cmd doctor` 看错误；缺 pycryptodome 多半就是 |

---

## 二、demo 模式跑不通

| 症状 | 原因 / 解法 |
|---|---|
| `no such table: xxx` | 没建库 → `renpu init` |
| `tuple index out of range` | 仁谱 的 demo 数据 bug → `renpu doctor --verbose` 看 stack，上 [github.com/jackyjinggit](https://github.com/jackyjinggit/...)/issues |
| 看不到 demo 数据 | `renpu ingest --demo` 没跑成功，看上面错误 |

---

## 三、接真微信库出错

| 症状 | 原因 / 解法 |
|---|---|
| `未配置微信源` | 见 INSTALL.md → Step 3 写配置 |
| `decryption failed (hmac_bad > 0)` | 微信 live 库在运行中被改了 → 关掉微信客户端再试，或复制一份副本解（**警告：副本可能丢最新消息**） |
| `找不到 db_key.txt` | 见 INSTALL.md → Step 2；或把 db_key.txt 拷到 `~/.config/renpu/db_key.txt` |
| `fresh_pull.py pull` 找不到 wc_export | 你的 wc_export 路径配错；或干脆配 `wc_live` 让 仁谱 自带解密 |
| 极慢（>3 分钟） | message 库很大（>300MB），首次解密要读完全部页；可考虑 `renpu ingest --days 30 --pull` 缩小窗口 |
| 表清单飘了一半 | SQLite 库损坏；用 `sqlite3 message.db .recover` 重建，或换上一份 fresh_ 库 |

### `wc_live` 自动探测不到？

`renpu doctor` 找不到但你知道路径在哪 → 直接写配置见 INSTALL.md。

### 不想自动探测 / 不想用 仁谱 自带解密器？

配 `wc_export` 让 仁谱 调你已有的 `fresh_pull.py`：
```json
{
  "wc_export": "/Users/you/my-fresh-pull-tools"
}
```

---

## 四、数据问题

| 症状 | 原因 / 解法 |
|---|---|
| 一个人都搜不到但确实加过 | 旧库过期 → `renpu ingest --pull` 重拉再查 |
| 关系边 0 | 没建 room_member（demo 数据该有的）；检查 groups |
| `who` 输出 `未找到` | 名字带空格/emoji 或全英文；用备注名重试 |
| `who` 出来有空字段 | 仁谱 不臆测：可能 contact 表里是别名等；用 `renpu people -q "名字"` 看 |
| 检索结果 0 | 索引里只存纯文本；语音/图片/表情不算 |
| `has_pii=1` 太多 | 你消息里手机号/身份证多，**这是正常的**（已自动脱敏） |

---

## 五、端口 / API

| 症状 | 原因 / 解法 |
|---|---|
| `serve` 起不来 | 端口被占，换端口：`renpu serve --port 9001` |
| `curl: connection refused` | 起 serve 的窗口没打开 / 端口被防火墙挡 |
| 跨机器访问 | **故意不让**。要跨机走 SSH 隧道：`ssh -L 8877:127.0.0.1:8877 you@local-machine` |
| API 返回 JSON 中文乱码 | 终端编码问题；用 `curl ... | python -m json.tool` 解码，或 `PYTHONIOENCODING=utf-8 renpu serve` |

---

## 六、删库重练

| 你想 | 做 |
|---|---|
| 完全重置 | 删 `%LOCALAPPDATA%\renpu\`（或对应 OS 路径里的 `renpu` 文件夹） |
| 只重置数据 | 删 `renpu.db`（其他保留） |
| 数据想搬家 | 改 `RENPU_DB_PATH` 环境变量 |
| 配置想清空 | 删 `config.json` |

删完 `renpu init && renpu ingest --demo` 重玩。

---

## 七、还得问人

| 症状 | 解法 |
|---|---|
| 上面的表里都没 | `renpu --verbose <你的命令>` 看 traceback，[github.com/jackyjinggit/issues](https://github.com/jackyjinggit/...)/issues |
| 库损坏了 | 关掉微信 → `sqlite3 message_0.db ".recover"` → 重新 sync |
| 上网找资料 | 见 README.md 「相关概念」里的底层微信解密 / 抽取 SOP |

---

## 八、健康检查脚本（自检汇总）

```bash
# 一句话体检输出
renpu doctor
```

或者更详细（直接调 `doctor` 输出原始数据）：
```bash
python -c "
import sys; sys.path.insert(0,'.')
from config import describe
import json
print(json.dumps(describe(), ensure_ascii=False, indent=2))
"
```

预期所有键都有值 + 配置文件路径存在。