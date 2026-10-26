# -*- coding: utf-8 -*-
# MiniMax 开放平台 Token 计划用量 -> 个人主页独立页生成器
# 用法: python gen_minimax_usage.py [新CSV路径]
# 不传参数则用默认下载路径；输出 minimax-usage.html（与 index.html 同目录）。
import csv
import sys
import os
from collections import defaultdict

DEFAULT_SRC = os.path.join(os.path.expanduser("~"), "Downloads",
                          "openplatform_tokenplanusage_token_plan_usage_2026-10-26T07_51_318863.csv")
SRC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

rows = []
with open(SRC, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        rows.append(row)

def num(x):
    x = (x or "").strip()
    if x in ("", "\u2014", "-"):
        return 0
    return int(float(x))

def fmt(n):
    return f"{n:,}"

mdl = defaultdict(lambda: {"in": 0, "out": 0, "cache": 0, "rows": 0, "kind": "Text"})
for r in rows:
    m = r["\u6a21\u578b/\u5de5\u5177"]; d = mdl[m]
    d["in"] += num(r["\u8f93\u5165Token"]); d["out"] += num(r["\u8f93\u51faToken"])
    d["cache"] += num(r["\u7f13\u5b58\u8bfb\u53d6"]); d["rows"] += 1
    if r["\u7c7b\u578b"] == "Image": d["kind"] = "Image"
    elif r["\u7c7b\u578b"] == "Video": d["kind"] = "Video"

day = defaultdict(lambda: {"in": 0, "out": 0, "cache": 0})
for r in rows:
    d = r["\u65f6\u95f4"][:10]; day[d]["in"] += num(r["\u8f93\u5165Token"])
    day[d]["out"] += num(r["\u8f93\u51faToken"]); day[d]["cache"] += num(r["\u7f13\u5b58\u8bfb\u53d6"])

tot_in = sum(v["in"] for v in mdl.values())
tot_out = sum(v["out"] for v in mdl.values())
tot_cache = sum(v["cache"] for v in mdl.values())
grand = tot_in + tot_out + tot_cache
billed = tot_in + tot_out
img = sum(num(r["\u6570\u91cf(\u5de5\u5177\u6b21/\u56fe\u7247\u5f20/\u89c6\u9891\u6761/\u8bed\u97f3\u5b57\u7b26)"]) for r in rows if r["\u6a21\u578b/\u5de5\u5177"] == "image-01")
vid = sum(num(r["\u6570\u91cf(\u5de5\u5177\u6b21/\u56fe\u7247\u5f20/\u89c6\u9891\u6761/\u8bed\u97f3\u5b57\u7b26)"]) for r in rows if r["\u6a21\u578b/\u5de5\u5177"] == "video-01")
w = sum(num(r["\u7f13\u5b58\u8bfb\u53d6"]) for r in rows)
weighted = sum(num(r["\u7f13\u5b58\u8bfb\u53d6"]) * num(r["cache\u547d\u4e2d\u7387"]) for r in rows)
hit = weighted / w

def pct(a, b):
    return (a / b * 100) if b else 0

models = sorted(mdl.items(), key=lambda kv: -(kv[1]["in"] + kv[1]["out"] + kv[1]["cache"]))
model_rows_html = ""
maxm = max((v["in"] + v["out"] + v["cache"]) for v in mdl.values())
for m, v in models:
    total = v["in"] + v["out"] + v["cache"]
    bar = pct(total, maxm)
    model_rows_html += (
        '      <tr>\n'
        '        <td>' + m + '<br><small class="muted">\u7c7b\u578b ' + v["kind"] + ' \u00b7 ' + str(v["rows"]) + ' \u65f6\u6bb5</small></td>\n'
        '        <td class="num">' + fmt(v["in"]) + '</td>\n'
        '        <td class="num">' + fmt(v["out"]) + '</td>\n'
        '        <td class="num">' + fmt(v["cache"]) + '</td>\n'
        '        <td class="num">' + fmt(total) + '</td>\n'
        '        <td style="min-width:160px"><div class="bar"><div class="bar-fill" style="width:' + ("%.1f" % bar) + '%"></div></div><small class="muted">' + ("%.1f" % pct(total, grand)) + '%</small></td>\n'
        '      </tr>\n'
    )

days = sorted(day.items())
day_rows_html = ""
maxd = max((v["in"] + v["out"] + v["cache"]) for v in day.values())
for d, v in days:
    total = v["in"] + v["out"] + v["cache"]
    bar = pct(total, maxd)
    day_rows_html += (
        '      <tr>\n'
        '        <td>' + d + '</td>\n'
        '        <td class="num">' + fmt(v["in"]) + '</td>\n'
        '        <td class="num">' + fmt(v["out"]) + '</td>\n'
        '        <td class="num">' + fmt(v["cache"]) + '</td>\n'
        '        <td class="num">' + fmt(total) + '</td>\n'
        '        <td style="min-width:160px"><div class="bar"><div class="bar-fill" style="width:' + ("%.1f" % bar) + '%"></div></div><small class="muted">' + ("%.1f" % pct(total, grand)) + '%</small></td>\n'
        '      </tr>\n'
    )

mind = min(day); maxd2 = max(day)
ndays = len(day)

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MiniMax 开放平台用量 \u00b7 蒋平个人站</title>
<meta name="description" content="蒋平 MiniMax 开放平台 Token 计划用量分析（__MIND__ ~ __MAXD__）：模型分布、每日节奏、缓存命中率。">
<meta name="theme-color" content="#1a73e8">
<style>
  :root {
    --accent-50:#e8f0fe;--accent-100:#d2e3fc;--accent-200:#aecbfa;--accent-300:#8ab4f8;
    --accent-400:#669df6;--accent-500:#4285f4;--accent-600:#1a73e8;--accent-700:#1967d2;
    --accent-800:#185abc;--accent-900:#174ea6;
    --ink-50:#fafafa;--ink-100:#f5f5f5;--ink-200:#eeeeee;--ink-300:#e0e0e0;
    --ink-400:#bdbdbd;--ink-500:#9e9e9e;--ink-600:#757575;--ink-700:#616161;
    --ink-800:#424242;--ink-900:#212121;
    --success:#2e7d32;--warning:#e65100;--error:#c62828;--info:#0277bd;
    --accent:var(--accent-600);--ink:var(--ink-900);--sub:var(--ink-600);
    --line:var(--ink-300);--bg:var(--ink-50);
    --space-1:4px;--space-2:8px;--space-3:12px;--space-4:16px;--space-6:24px;
    --space-8:32px;--space-12:48px;--space-16:64px;
    --radius-md:8px;--radius-pill:999px;
    --shadow-md:0 1px 4px rgba(0,0,0,.08);
    --text-sm:14px;--text-base:16px;--text-md:18px;--text-xl:20px;--text-2xl:32px;
    --font-sans-cn:-apple-system,"Noto Sans SC","Microsoft YaHei",sans-serif;
  }
  *,*::before,*::after{box-sizing:border-box}
  body{font-family:var(--font-sans-cn);background:var(--bg);color:var(--ink);line-height:1.7;margin:0;padding:0 var(--space-4) var(--space-16)}
  @media(min-width:768px){body{padding:0 var(--space-6) var(--space-16)}}
  h1{font-size:var(--text-2xl);font-weight:600;margin:var(--space-6) 0 var(--space-2)}
  h2{font-size:var(--text-xl);margin:var(--space-8) 0 var(--space-3)}
  p{margin:0 0 var(--space-4)}
  a{color:var(--accent-700);text-decoration:none}
  a:hover{text-decoration:underline}
  nav{position:sticky;top:0;background:rgba(250,250,250,.95);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:10;margin:0 calc(var(--space-4)*-1);padding:var(--space-3) var(--space-4)}
  @media(min-width:768px){nav{margin:0 calc(var(--space-6)*-1);padding:var(--space-3) var(--space-6)}}
  nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:var(--space-1)}
  nav a{display:inline-block;padding:var(--space-1) var(--space-3);border-radius:var(--radius-pill);font-size:var(--text-sm);color:var(--sub)}
  nav a:hover{background:var(--accent-50);color:var(--accent-700);text-decoration:none}
  .muted{color:var(--sub);font-size:var(--text-sm)}
  .card{background:#fff;border-radius:var(--radius-md);padding:var(--space-6);box-shadow:var(--shadow-md);margin:var(--space-4) 0}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--space-4)}
  .grid .card{margin:0}
  .stat-num{font-size:var(--text-2xl);font-weight:600;color:var(--accent-700);line-height:1.1}
  .stat-num small{font-size:var(--text-base);color:var(--ink-700)}
  table{width:100%;border-collapse:collapse;font-size:var(--text-sm);background:#fff;border-radius:var(--radius-md);overflow:hidden;box-shadow:var(--shadow-md);display:block;overflow-x:auto;white-space:nowrap}
  th,td{text-align:left;padding:var(--space-3) var(--space-4);border-bottom:1px solid var(--line);vertical-align:top;min-width:120px}
  th{background:var(--ink-100);font-weight:600;color:var(--ink-800)}
  tr:last-child td{border-bottom:none}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  @media(min-width:768px){table{display:table;white-space:normal}}
  .bar{background:var(--ink-100);border-radius:var(--radius-pill);height:10px;overflow:hidden}
  .bar-fill{background:linear-gradient(90deg,var(--accent-400),var(--accent-600));height:100%}
  .note{background:var(--accent-50);border-left:4px solid var(--accent-600);border-radius:var(--radius-md);padding:var(--space-4) var(--space-6);margin:var(--space-4) 0}
  .note p{margin:0 0 var(--space-2)}
  .note p:last-child{margin-bottom:0}
  footer{border-top:1px solid var(--line);margin-top:var(--space-12);padding-top:var(--space-6);font-size:var(--text-sm);color:var(--sub)}
</style>
</head>
<body>
<nav><ul>
  <li><a href="index.html">首页</a></li>
  <li><a href="index.html#data">数据</a></li>
  <li><a href="library.html">扩展阅读库</a></li>
  <li><a href="en/index.html">English</a></li>
</ul></nav>

<section>
  <h1>MiniMax 开放平台用量</h1>
  <p class="muted">统计窗口 __MIND__ ~ __MAXD__（__NDAYS__ 天）\u00b7 数据来源：MiniMax 开放平台 Token 计划用量导出 CSV（客户端只读授权，无内容/无 PII）。</p>
  <p class="muted">这套数字不是成就，是样本量——长上下文 + 高缓存命中率，是把「三个月真实协作」跑顺的算术证据。</p>
</section>

<section>
  <div class="grid">
    <div class="card"><div class="stat-num">__GRAND__<small> 亿</small></div><p class="muted">总处理 token<br>（输入+输出+缓存读取）</p></div>
    <div class="card"><div class="stat-num">__BILLED__<small> 亿</small></div><p class="muted">计费 token<br>（仅输入+输出）</p></div>
    <div class="card"><div class="stat-num">__CACHE__<small> 亿</small></div><p class="muted">缓存读取<br>（命中后从缓存取，通常折扣/免费）</p></div>
    <div class="card"><div class="stat-num">__HIT__<small>%</small></div><p class="muted">加权缓存命中率</p></div>
    <div class="card"><div class="stat-num">__IMG__<small> 张</small></div><p class="muted">image-01 图片生成</p></div>
    <div class="card"><div class="stat-num">__VID__<small> 条</small></div><p class="muted">video-01 视频生成</p></div>
  </div>
</section>

<section>
  <h2>按模型 / 工具</h2>
  <p class="muted">M3-512k 是绝对主力（长上下文主力模型）；M3.1-Flash 自 10/23 起放量；纯文本占了绝大多数，图片/视频是小头。</p>
  <table>
    <thead><tr><th>模型 / 工具</th><th class="num">输入</th><th class="num">输出</th><th class="num">缓存读取</th><th class="num">合计</th><th>占比（占窗口总量）</th></tr></thead>
    <tbody>
__MODEL_ROWS__    </tbody>
  </table>
</section>

<section>
  <h2>按日节奏</h2>
  <p class="muted">峰值出现在 10/25（单日破 12 亿），整体呈「项目冲刺日高、间歇日低」的工作波次；10/08、10/19 为明显低谷。</p>
  <table>
    <thead><tr><th>日期</th><th class="num">输入</th><th class="num">输出</th><th class="num">缓存读取</th><th class="num">合计</th><th>强度（相对峰值）</th></tr></thead>
    <tbody>
__DAY_ROWS__    </tbody>
  </table>
</section>

<section>
  <div class="note">
    <p><strong>怎么读这份数据</strong></p>
    <p>1. 「缓存读取」__CACHE__ 亿，是真正的大头——它代表长上下文被反复复用（同一段系统提示 / 长文档被反复带进对话），命中后按折扣或免费计费。也就是说：<strong>实际花钱的只有「输入 + 输出」\u2248 __BILLED__ 亿 token</strong>，长上下文把成本压了下来。</p>
    <p>2. 加权缓存命中率 __HIT__%，说明绝大多数请求命中了既有缓存，符合长上下文 + 提示缓存（context caching）的运行方式。</p>
    <p>3. 这份是 <strong>2026-10-06 ~ 10-25 的 MiniMax 单一来源</strong>，与首页「数据」段「~130 亿 token / ~8 万轮（自 2026 年 4 月累计，多来源）」<strong>口径不同、不互相覆盖</strong>。本窗口 20 天即产生约 __GRAND__ 亿，提示全量累计数可能需要刷新。</p>
    <p>4. 本页为<strong>增量件</strong>：每次从开放平台导出新 CSV，重跑生成脚本即可刷新，不改动既有设计。</p>
  </div>
</section>

<footer>
  <p>数据源：MiniMax 开放平台 Token 计划用量 CSV（只读导出）\u00b7 最后生成：__MAXD__</p>
  <p>返回 <a href="index.html">个人站首页 ↗</a></p>
</footer>
</body>
</html>
"""

HTML = (HTML
    .replace("__MIND__", mind).replace("__MAXD__", maxd2).replace("__NDAYS__", str(ndays))
    .replace("__GRAND__", "%.1f" % (grand/1e8)).replace("__BILLED__", "%.2f" % (billed/1e8))
    .replace("__CACHE__", "%.1f" % (tot_cache/1e8)).replace("__HIT__", "%.1f" % hit)
    .replace("__IMG__", str(img)).replace("__VID__", str(vid))
    .replace("__MODEL_ROWS__", model_rows_html).replace("__DAY_ROWS__", day_rows_html))

out = os.path.join(OUT_DIR, "minimax-usage.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print("written:", out)
print("grand=%.1f亿 billed=%.2f亿 cache=%.1f亿 hit=%.1f%% img=%d vid=%d days=%d" % (
    grand/1e8, billed/1e8, tot_cache/1e8, hit, img, vid, ndays))
