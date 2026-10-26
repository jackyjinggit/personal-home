# QUICKSTART · 5 分钟跑通

## Step 1 · 装 Python 依赖

```bash
pip install pycryptodome
```
> 唯一必需的依赖。

## Step 1.5 · 【可选】先一键看看效果

```bash
renpu tour
```

1.6 秒跑完，会在临时目录产出一个关系图谱 HTML 和一份摘要报告。
全程用合成数据，不碰你的微信。看一眼再决定要不要往下装。

---

## Step 2 · 把 `renpu` 命令加进 PATH

**Windows（PowerShell）**
```powershell
# 把 仁谱仓的 bin/ 加到 PATH（一次性）
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$((Resolve-Path .\bin).Path)", "User")
```
或者直接双击 `bin/renpu.cmd` 用。

**macOS / Linux（bash）**
```bash
echo 'export PATH="$PWD/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
# 或者用脚本直接装
bash scripts/install.sh
```

## Step 3 · 体检

```bash
renpu doctor
```
应看到 `✅ 一切就绪` 或 `⚠️ 缺 pycryptodome` 之类明确指引。

## Step 4 · 建库 + 灌 demo

```bash
renpu init
renpu ingest --demo
```
应看到：
- `✅ 仁谱库就绪：%LOCALAPPDATA%\renpu\renpu.db`（或对应 OS 路径）
- `✅ Demo 注入完成：人 10 · 消息 2000 · 关系边 20`

## Step 5 · 随便玩

```bash
renpu who 林夏                  # 一人档案
renpu people --days 7 --limit 5   # 近 7 天活跃
renpu search "黑客松"              # 检索
renpu edges                       # 人际边
renpu feed --days 3               # 近期消息流
renpu note "AAA 层同学 · 已能约饭" --name 林夏 --kind ai_note
renpu note "下周一回访确认 demo" --name 苏见白 --todo
renpu todo
```

## Step 6 · 让任何 agent 接入（可选）

```bash
renpu serve --port 8877
```
另一个窗口：
```bash
curl -s "http://127.0.0.1:8877/api/who?name=%E6%B7%AE%E6%99%93%E9%9B%AF" | python -m json.tool
curl -s "http://127.0.0.1:8877/api/people?days=30" | python -m json.tool
```

> Web agent 接入 仁谱 让其能回答「我跟他什么关系」类问题，详见 README.md 「两个数据源」与 `SKILL.md`。

## 完事

你已经装好 仁谱 并能用了。继续深入：

- 接你真微信库 → [INSTALL.md](INSTALL.md)
- 排障 → [TROUBLESHOOT.md](TROUBLESHOOT.md)
- 自定义数据存储位置 / 端口 / 任意配置 → 见 `config.py` 头部

> 卸载（想删库重练）：删 `%LOCALAPPDATA%\renpu\`（或对应 OS 路径里的 `renpu` 文件夹）。