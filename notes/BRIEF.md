# 写作说明（给每位作者）

仓库：~/Projects/us-finance-law（本机，不要 git push、不要发布任何东西）。
书名：《美国金融业法律研究：规则从何而来》。证券篇共 12 章；第 1 章已写好，是样板：
- 正文：chapters/02-s01-卖的人比买的人知道得多.md
- 图：figs/s01-*.html
- 参考上一本书的一章写法：/private/tmp/claude-501/-Users-a9527/1a82fa3e-0dd5-40eb-8298-c68c70e5250f/scratchpad/pfa.C0ck/r/gen/08-证券要能卖出去.md 与它的图 figs/g08-*.html；写作方法见同目录 chapters/A2-本书的写法.md

## 写法
1. 生成式推演：每章只引入一个新问题，按「问题 → 市场的回应 → 法律的回应 → 留下的问题」展开。史实与判例作为出处，不写成编年史。
2. 结构照第 1 章：frontmatter（file/kind/no/title/subtitle/part/asof/desc）、版本表、`<!-- body -->`、开头一段引言（>）、「## 一、…」等七八个语义块、穿插「**今天的对应。**」段落（落到今天美国线上券商与投资类 App 的业务上）、倒数第二节「这一步留下的问题」（配一张 sXX-next 图，指向后续章节）、最后一节「对产品的含义」（三条，尤其是对线上券商与 AI 产品的含义）、「## 参考文献」。
3. 规则卡：每章 2–3 张，格式与第 1 章完全相同（:::原理 名称 … :::，首行一句话表述，其后字段：学科、类型、地位、约束、前提、提出、问题）。「地位」只写有出处的事实（条文编号、取代了什么、被哪个判例确立），不写「最重要」「里程碑」之类评价。规则出现在推演完成之后，不先抛名称。第 12 章重新检验已有规则时用 `:::重跑 名称`，另加字段「重跑：…」。
4. 语言：朴素的中文书面语，结论先行、句子完整、写具体数字与日期；不用比喻堆砌、排比、口号；不写「值得注意的是」「综上所述」「一句话总结」「至关重要」「里程碑」「深刻」等 AI 腔；不用公司黑话（赋能、抓手、闭环、打通）。人名用通行中文译名（如阿克洛夫、布兰代斯），判例写「X 诉 Y 案」并在参考文献给出原始引注；首次出现的机构写全称再用简称，例如「美国证券交易委员会（SEC）」「金融业监管局（FINRA）」。
5. 长度：每章正文约 3,500–5,500 个汉字；4–6 张图。

## 事实核实（硬性要求）
- 每一个条文编号、规则编号、判例名称与引注、年份、金额门槛、比例、生效与合规日期，都要用 WebSearch / WebFetch 在一手或可靠来源（sec.gov、finra.org、federalregister.gov、ecfr.gov、law.cornell.edu、supreme.justia.com、fincen.gov、federalreserve.gov）核实。
- 资料截至 2026 年 11 月。2023–2026 年有过变化的规则，必须查到最新状态（被采纳、推迟、撤回、被法院撤销），并写明日期。查不到可靠来源的说法，删去或改为不涉及具体数字的说法。
- 每章写一份核实清单：notes/sXX-sources.md，逐条列出「说法 — 来源 URL — 核实结论」，并单列「仍不确定的点」。

## 交互图
- 每张图一个文件 figs/sXX-名称.html，结构照第 1 章：`<figure><div class="card">…</div></figure>` + `<style>` + `<script>(function(){…})();</script>`。
- **类名与 id 必须带本图独有的前缀**（如 s05-res 图里的类名都以 r5 开头），避免与其他图冲突；不要使用 .tl .cp .mm .ex .sk 等通用短名。
- 只用 book.css 的变量：--ink --bg --card --quote --accent --accent-soft --muted --faint --line。不引入外部库。
- 图要说明机制、可以操作（点选、拖动、切换）。图中的每个数字都要与正文一致；示意性的数字标「示意」。
- 正文中单独一行 `{{fig:sXX-名称}}` 插入。

## 检查
- 写完运行 `cd ~/Projects/us-finance-law && python3 build.py`，确认无报错。
- 用无头 Chrome 截图检查自己的章节页，例如：
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1300,5000 --virtual-time-budget=4000 --screenshot=/private/tmp/claude-501/-Users-a9527/1a82fa3e-0dd5-40eb-8298-c68c70e5250f/scratchpad/shots10/law-sXX.png "file://$HOME/Projects/us-finance-law/site/sXX.html"
  然后用 Read 查看截图，确认图正常渲染、没有错位。
- 只修改自己负责的文件，不改 build.py、不改别人的章节和图。

## 交付
最后回复：写了哪些文件；每章三五条最关键的核实结论（含 2023–2026 年的最新状态）；仍不确定、需要作者确认的点。
