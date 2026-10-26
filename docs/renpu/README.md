# 仁谱 Renpu

> **人脉的谱系。** 把你的联系人变成一张图谱 —— 谁是谁的人、在哪些群共现、
> 什么时候答应过什么、上次聊到哪里。任何 agent 都能查、能写。

```
renpu who 林夏        # 一个人的完整档案：关系 + 群 + 承诺 + 时间线
renpu edges             # 关系谱：谁跟谁在多少个群里共现
renpu people --days 7   # 最近还有来往的人
```

---

## 这东西解决什么

你有过这种时刻吗——

> 「我跟 XXX 什么关系来着？」

然后你翻了半小时聊天记录，或者干脆没想起来。

仁谱把你微信里的联系人变成**结构化的关系资产**：谁和谁在同一个群、谁答应过你什么、
上次聊到哪里、哪个人最近冷了。这些答案应该是**一次查询**，不是一次考古。

---

## 和「微信日报工具」的区别（重要，先看这段）

市面上已经有做得不错的同类项目（比如做每日情报日报的思路），它们回答的是：

> 「**有什么该做**」—— 今天有哪些消息没回、有哪些商机、今天要处理哪 10 件事

仁谱回答的是另一个问题：

> 「**他是谁的人**」—— 这个人在我的关系网里是什么位置、跟谁是一伙的、
> 我们的关系从哪一步开始变的、我欠他什么

| | 仁谱 Renpu | 情报日报类工具 |
|---|---|---|
| 核心对象 | **人（关系）** | 消息（情报） |
| 主输出 | 关系谱 + 事件 + 待办 | 日报 HTML + 商机清单 |
| 查询「X 是谁」 | ✅ 档案 + 群 + 关系边 | ⚠️ 只能捞出 X 说过的话 |
| 关系推理 | ✅ **群共现建图**（谁跟谁一起出现过） | ❌ 无 |
| 跨渠道统一人实体 | ✅ 已预留（同一人多渠道合并） | ❌ 按会话切片 |
| 状态 | 早期 v0.1 | 部分已商业化 |

**一句话**：日报工具帮你处理今天的事，仁谱帮你记住你这个人。
两者不冲突，可以并存。

---

## 5 分钟上手

```bash
# 1. 装依赖（唯一必需项）
pip install pycryptodome

# 2. 体检 + 建库 + 零配置体验
renpu doctor && renpu init && renpu ingest --demo

# 3. 随便玩
renpu who 林夏          # 一人档案
renpu edges               # 关系谱
renpu search 黑客松        # 全文检索
renpu feed --days 3       # 近期消息流
renpu serve --port 8877   # 起本地 API，任何 agent 都能调
```

> 详细：[QUICKSTART.md](QUICKSTART.md) · 接真微信：[INSTALL.md](INSTALL.md) · 卡住了：[TROUBLESHOOT.md](TROUBLESHOOT.md)

---

## 它是什么 / 不是

**是**：本地优先、渠道无关、agent 可调用的关系数据中枢。微信是第一个 adapter，不止微信。

**不是**：
- 不是抽取脚本（不是「抽出→存 md」的旧模式）
- 不是云服务（库全程在本机，不上传）
- 不是关系分析 AI（结论由你和你的 agent 写回 `event`/`todo` 表，程序不替你下判断）
- 不是 CRM（它不替你维护关系，只让你能问、能写）

---

## 架构

```
   微信 4.x 本地库（只读，绝不写）
        │  内置解密器（SQLCipher4 + WAL merge）
        ▼
   fresh_<YYYY-MM-DD>/{contact, message_0, session, contact_fts}.db
        │  adapters/wechat.py
        ▼
 ┌──────────────────────────────┐
 │  renpu.db（SQLite WAL）       │  ← 唯一真源
 │  person / identity           │     人（跨渠道统一实体）
 │  tag / person_tag            │     标签（微信标签 + 你自己打的）
 │  room / room_member          │     群与成员 ← 关系推理的原料
 │  conversation                │     会话
 │  msg_index / msg_fts         │     消息索引（FTS 可检索 + PII 已脱敏）
 │  event / edge / todo         │     关系事件 / 关系谱边 / 待办
 └──────────────────────────────┘
        │                          │
   renpu（人/终端）           renpu serve（agent）
   renpu who 姓名              GET /api/who?name=...
   renpu edges                 GET /api/edges
   renpu note "..."            POST /api/note
```

**关系谱（edge）怎么来的**：两个联系人同时出现在 N 个群里 → 建立一条权重 N 的边。
不需要任何人手动录入，摄取时自动算出来。

**社区（圈子）怎么来的**：群共现天然形成社区。仁谱从 `room_member` 反推共同群，
把「主要群相同的人」归为一个圈子，图上同色 = 同一个圈子，一眼看出谁跟谁是一伙的。

**边上标的「N 群」**：这条关系共同出现在几个群里。数据来自 `edge.rooms`，
由 `room_member` 全量事实反推，保证和权重一致（不会出现「权重说 3 个群、列表只列 1 个」）。

**时间轴怎么来的**：`person.first_seen`（首次进入你人脉的时间）由 `msg_index` 与
`room_member` 双源反推回填，覆盖全库 68%。图上拖动滑块 = 拖动时间，
只看当时已经进入你人脉的人，看圈子怎么一步步长出来。

**中文搜索怎么做的**：SQLite FTS5 的默认分词器对中文按**单字**切分，
整词 `MATCH '黑客松'` 会命中 **0 条**（实测 demo 库 2000 条消息）。
所以搜索统一走 `core.search_messages()`：关键词加 `*` 前缀做前缀匹配，
FTS 仍为 0 时回退 `LIKE` —— 保证「搜得到」永远成立。

**3D 关系圈**：点某人 → 以他为中心，把关系圈摆成球面（越靠中心 = 关系越强）。
用 SVG 手写透视投影 + 画家算法，零第三方依赖。
不用 CSS 3D transform —— 它没有真正的 3D 渲染管线，实测 886 条边里 884 条
横穿侧边栏、节点被拉成斜线阵列、UI 层被吃掉。

---

## 数据落在哪

跨平台默认（什么都不用配）：

| 系统 | 数据库 | 配置文件 |
|---|---|---|
| Windows | `%LOCALAPPDATA%\renpu\renpu.db` | `%LOCALAPPDATA%\renpu\config.json` |
| macOS | `~/Library/Application Support/renpu/renpu.db` | 同目录 `config.json` |
| Linux | `~/.local/share/renpu/renpu.db` | `~/.config/renpu/config.json` |

想放网盘或工作区？设 `RENPU_DATA_HOME=~/vault/people`。

---

## 两个数据源

| Source | 需要配置吗 | 说明 |
|---|---|---|
| **demo** | ❌ 不用 | 合成数据（10 人 / 2000 消息 / 33 条关系边）。先跑这个验证产品合不合适。 |
| **wechat** | 配 `wc_live` 路径 | 你自己的微信 4.x 库。只读，摄取 30-90 秒。 |

> **demo 数据里所有姓名都是虚构的**（林夏 / 苏见白 / 陈屿 / 周斯年 …），
> wxid 一律是 `wx:demo_*` 前缀，关系定性也全是通用标签。
> 它不包含任何真实联系人——这是公开发布的硬要求，不是可选项。

---

## 桌面工作台

`desktop2.py` 是完整工作台（tkinter，零第三方依赖）：

| 导航 | 能干什么 |
|---|---|
| 总览 | 五个统计卡 + 聊得最多的人 + 待跟进 |
| 联系人 | 表格列表，选中看右栏详情，**双击打开完整档案页** |
| 关系图谱 | 生成并打开 2D 图谱（可拖时间轴看圈子扩张） |
| 3D 关系圈 | 聚焦某人，生成 3D 球面 |
| 待办与承诺 | 列表，双击标记完成 |
| 事件 | 时间线列表 |
| 全文搜索 | 中文全文检索 |
| Agent 接入 | 启停本机 API，列出可用端点 |
| 数据与设置 | 切换演示库/真实库、配置微信源、摄取数据 |

**数据主权**：默认只连**演示库**；接真实微信必须用户显式填 `db_storage` 目录，程序不自动读。

## 命令全表

```text
renpu doctor                      环境自检（跑不起来先看这个）
renpu tour                        一键体验：零配置跑一遍，出图谱 + 报告
renpu init                        建库
renpu ingest [--demo] [--days 90] 摄取；--demo 零配置；--pull 先解密再摄取
renpu stats                       总览
renpu people [-q 词] [--days N]   人列表
renpu who <姓名>                   单人档案：档案+近期对话+群+关系谱+待办+事件
renpu edges [--limit N]           关系谱（群共现强度）
renpu graph [--limit N] [--focus connected|active] [--share]
                              关系图谱 HTML：交互式、单文件、零依赖
                              同色=同一圈子 · 边上标共同群数 · 点击某人高亮其关系圈
                              底部时间轴：拖动看圈子随时间扩张
renpu graph3d [--person 名字] [--limit N] [--share]
                              3D 关系圈 HTML：聚焦某人的关系结构
                              球面布局（越靠中心=关系越强）· 手写透视投影 · 零依赖
renpu profile 名字 [--share] [--out PATH]
                              人物档案页 HTML：一个人的完整档案
                              关系人 · 时间线 · 近期对话 · 承诺 · 事件
                              --share 真名脱敏 + 时间降级到天（可安全发给别人）
renpu graph [--limit N] [--focus connected|active] [--share] [--out PATH]
                                  关系图谱 HTML（交互式，单文件，可直接分享）
                                  --share 群名脱敏 + 隐藏消息数（可安全发人）
renpu search <关键词>              全文检索
renpu feed [--days N]             近期消息流
renpu rooms [--limit N]           群列表
renpu todo                        待办清单
renpu note "内容" [--name 姓名] [--kind promise] [--todo]
renpu todo --done <id>            关待办
renpu serve [--port 8877]         起本地 HTTP API（仅 127.0.0.1）
renpu --json <cmd>                结构化输出（给程序用）
renpu --verbose <cmd>             出错时打印完整 traceback
```

---

## 硬纪律（代码里就守着，不是建议）

1. **PII 红线**：库在用户目录，不入 git、不上云、不进公开线。入库自动脱敏手机号/身份证/卡号。
2. **只读源库**：全程零写入你的微信数据。解密快照落在仁谱自己的目录里。
3. **判断不臆测**：`person.tier/circle/org` 这些「他是什么人」的字段，程序不自动填——那是你的判断位。
4. **缺口不吞**：语音（加密字节）、撤回（不可复原）如实说「未读到」，不假装读懂了。
5. **API 只绑本机**：`127.0.0.1`，不监听 `0.0.0.0`。要跨机自己走隧道，那是显式动作不是默认。

---

## 已知边界

| 项 | 状态 |
|---|---|
| 语音消息 | 加密字节，未转写 = 缺口 |
| 撤回消息 | 不可复原 = 缺口 |
| 图片/视频/文件 | 只存类型不存内容 |
| 精确加好友时间 | 源库无此字段，不做推断 |
| 朋友圈（sns） | 未接（可作下个 adapter） |
| PC 未同步的消息 | 库里没有 ≠ 对方没发 |

---

## 接下一个数据源

新建 `adapters/<channel>.py`，实现 `ingest()` 调 `core.py` 的六个域函数即可，
CLI 和 API 一行都不用改。字段已预留：`identity(channel, channel_id)` 一人多渠道、
`person.person_key` 跨渠道稳定 ID。

---

## 开源层与商业层

本项目采用**开放核心 + 商业层**结构。

### 开源（AGPL-3.0-only）

| 层 | 内容 |
|---|---|
| 存储模型 | SQLite schema、六域数据模型、关系边推导算法 |
| 数据入口 | 微信 4.x 只读 reader / 解密器、adapter 接口 |
| 接口 | 命令行 CLI、本地 HTTP API（127.0.0.1） |
| 文档测试 | 全部文档、`tests/test_smoke.py`、demo 数据 |

**这些层你可以自由使用、修改、二次分发**——AGPL 允许，署名义务除外。

### 商业层（另行授权）

| 层 | 状态 |
|---|---|
| AI 解读引擎（`digest` / 关系摘要 / 主动提醒） | 计划中 · 闭源 |
| 企业版（数据保留策略、审计日志、团队多库） | 计划中 · 闭源 |
| 托管服务 | 暂不做 |

闭源需求（嵌入闭源产品 / 白标 / 私有化交付）请看 `LICENSE` 末尾的
**RENPU ADDITIONAL TERMS NOTICE**，或开 issue 询价。

### 为什么要这么分

仁谱的**开源层**解决「能不能跑起来」——这是传播的引擎，开放才能传得远。
仁谱的**商业层**解决「值不值得持续用」——这是价值所在，开放了护城河就没了。

**单独拿走开源层能做什么**：一个能读你微信、能建关系图谱的本地工具。很好用。
**单独拿走开源层不能做什么**：让这套数据每天主动告诉你该联系谁。这才是长期价值。

---

## 许可

**AGPL-3.0-only** · 蒋平 Jacky Jiang · https://github.com/jackyjinggit/renpu

选 AGPL 而非 MIT/Apache，是因为本项目的核心接口是**网络接口**（本地 HTTP API）。
AGPL §13 要求：基于本项目的修改版通过网络提供服务时，必须向使用者提供对应源码。

**闭源集成、白标、商业授权**见 `LICENSE` 末尾 RENPU ADDITIONAL TERMS NOTICE。

转载或二次分发本 Skill 时，请保留出处声明与上游链接（AGPL §5(a) 署名义务）。