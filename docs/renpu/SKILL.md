---
name: renpu-relationship-hub
description: 仁谱 Renpu · 人脉的谱系。任何人际类提问（X 是谁 / 我跟 X 什么关系 / 上次聊了什么 / 该回谁 / 谁跟谁是一伙的）先查 renpu，不要重跑微信解密。提供 CLI（renpu）与本地 API（127.0.0.1:8877）双入口。触发词：renpu、仁谱、人际关系、人脉、关系谱、X是谁、什么关系、上次跟谁聊、该回谁、跟进某人、谁介绍谁、共现、群共现。
  触发关键词：renpu、仁谱、人际关系、人脉、关系谱、X 是谁、什么关系、上次跟谁聊、该回谁、跟进某人、谁介绍谁、共现、群共现、who is X、how do I know X、followup、relationship graph。
allowed-tools: 
disable-model-invocation: false
user-invocable: true
version: "0.2.1"
---

<!--
  ┌─────────────────────────────────────────────────────────────┐
  │  仁谱 Renpu · 由 蒋平 Jacky Jiang (jackyjinggit) 原创        │
  │  项目主页：https://github.com/jackyjinggit/renpu             │
  │  License: AGPL-3.0-only                                     │
  │                                                              │
  │  ⚠️ 转载/二次分发本 Skill 或其代码时，请保留：                │
  │    ① 本出处声明与上游仓库链接                                 │
  │    ② AGPL-3.0-only 许可（衍生作品同样适用）                 │
  │    ③ 在文档中标注「基于 Renpu」并说明改动                    │
  │                                                              │
  │  这不是软性请求，是 AGPL §5(a) 的署名义务。                  │
  └─────────────────────────────────────────────────────────────┘
-->

# 仁谱 Renpu（agent 接入指南）

> **仁谱 Renpu** · 人脉的谱系 · 原作者 **蒋平 Jacky Jiang** · https://github.com/jackyjinggit/renpu
> License: **AGPL-3.0-only**（衍生作品须同样开放源码并保留署名）

> 人脉的谱系。做的是「**他是谁的人**」，不是「今天有什么该做」。
> 任何人际类提问，**先查 renpu**，不要重跑解密流水线——解密一次约 6 秒 + 摄取 30-90 秒，
> 问一个人却重跑全流程是烧 token 的反面教材。

## 何时用

- 「X 是谁 / 我跟 X 什么关系 / 上次跟 X 聊了什么」
- 「X 和 Y 怎么认识的 / 谁跟谁是一伙的 / 他们在几个群里一起出现过」→ 查 `edges`（群共现建图）
- 「最近哪些人没联系 / 谁该回了 / 有哪些待跟进」→ 查 `people --days` / `todo`
- 「我答应过 X 什么」→ 查 `todo` + `event`
- 任何需要「先知道这个人」的前置动作（写外发内容、做画像、约人）

## 两个入口

### 1 · CLI（默认）
```bash
renpu doctor                  # 环境自检
renpu init                    # 建库（首次）
renpu ingest --demo           # 零配置演示数据
renpu ingest                  # 真实微信摄取（需 wc_live / wc_export 已配）
renpu who 林夏              # 单人档案（档案+近期对话+群+关系谱+待办+事件）
renpu people --days 7         # 近 7 天有来往的人
renpu edges                   # 关系谱（群共现强度）
renpu search 黑客松            # 全文检索
renpu feed --days 3           # 近期消息流
renpu rooms                   # 群列表
renpu todo                    # 待跟进清单
renpu stats                   # 数据总览
renpu --json who 林夏        # 结构化输出（程序化处理时加 --json）
```

### 2 · API（并发 / 程序化，需先起服务）
```bash
renpu serve --port 8877       # 只绑 127.0.0.1

curl "http://127.0.0.1:8877/api/who?name=林夏"
curl "http://127.0.0.1:8877/api/people?days=30&limit=20"
curl "http://127.0.0.1:8877/api/edges?limit=20"
curl -X POST http://127.0.0.1:8877/api/note \
     -d '{"text":"他答应引荐XX","name":"张三","kind":"promise"}'
```
端点全表：`stats | people | who | search | feed | rooms | edges | todos`，POST：`/api/note`、`/api/todo/close`。

## 写回纪律（结论要落库，不要只在对话里说）

分析完对话得出的关系判断，**必须写回**，否则下次窗口又从零开始：
```bash
renpu note "内容摘要" --name 张三 --kind promise   # 事件（kind: promise/intro/meet/gift/first_talk/recontact/breach）
renpu note "下周回访" --name 张三 --todo            # 待办
renpu todo --done 5                                 # 关待办
```
每条结论由你负责带 `evidence`（原话引用）——**结论必须可溯源回原话**，不许臆测。

## 定位边界（别越界用）

仁谱回答「**他是谁的人**」，不回答「**今天该做什么**」。
如果你被要求生成每日待办清单/商机雷达，那不是仁谱的活——本工具没有那个能力，不要假装有。

## 数据现状

随用户配置变化。**时效敏感的任务先 `renpu ingest --pull`**（拉最新解密快照再摄取，约 30-90 秒），
否则可能拿到几周前的对话——「读旧库漏掉 51 条新对话导致关系定性全变」是本机实证过的坑。

## 硬纪律（不可绕过）

1. **PII 红线**：库默认在用户级目录，不出本机、不入 git、不进公开线、不发飞书/企微。入库自动脱敏手机号/身份证/卡号。
2. **给用户看的一律昵称 + 微信号**，绝不出现 wxid（微信不支持 wxid 搜人，那串只在库里有意义）。仁谱渲染层已强制此规则。
3. **判断留空标「待深挖」**，禁止用常识补全他人身份/组织/动机。
4. **缺口不吞**：语音（加密字节）、撤回（不可复原）如实说「未读到」，别假装读懂了。
5. **不代写他人画像**：`tier/circle/org` 是用户与人工的判断位，程序不自动填。
6. **源库只读**：全程不写微信 live 库与解密快照。

## 排障

| 症状 | 解法 |
|---|---|
| `no such table` | 库没建 → `renpu init` |
| `未配置微信源` | 先 `renpu ingest --demo`；或按 INSTALL.md 配 `wc_live` |
| 谁也搜不到但确有此人 | 大概率是旧库 → `renpu ingest --pull` 再查 |
| `ModuleNotFoundError: Crypto` | `pip install pycryptodome` |
| 端口被占 | `renpu serve --port 9001` |
| 想看完整报错 | 同命令加 `--verbose` |

相关：底层微信解密 / 抽取 SOP（见 README.md「相关概念」）。