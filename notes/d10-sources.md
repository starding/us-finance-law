# 分解式「发行人」核实清单（d10）

核实日期：2026-11-17。本页数字与第 2 章（s02）、第 3 章（s13）一致，来源见 notes/s02-sources.md、notes/s13-sources.md；以下只列本页新增或需要单独说明的说法。

## 已核实
- 10-K 期限 60/75/90 天、10-Q 40/45 天 — 见 s02-sources（律所日历）。
- 8-K 一般 4 个工作日；7.01、8.01 除外；1.05 自认定重大起算；5.07 结果确定后 4 个工作日 — https://www.sec.gov/files/form8-k.pdf — 属实。
- 10-K 第三部分可引用财年结束后 120 天内提交的最终委托书（Form 10-K 一般指示 G(3)）— 通行知识，未单独打开表格原文。
- Form 3/4/5 期限 — https://www.sec.gov/rules/final/34-46421.htm — 属实。
- 10b5-1 冷静期与 2023-02-27 生效 — 见 s07-sources — 属实。
- 13D 新期限生效日 2024 年 2 月 5 日（联邦公报 2023-11-07 刊登后 90 天）；13G 新期限 2024-09-30 — https://www.sec.gov/newsroom/press-releases/2023-219 （90 天规则）；具体日期据律所摘要 https://www.skadden.com/insights/publications/2024/09/new-schedule-13g-accelerated-filing-deadlines — 属实。
- 要约收购 20 个工作日、2026-04-16 豁免令 10 个工作日；目标公司 10 个工作日 — 见 s13-sources — 属实。
- 气候规则结构：S-K 第 1500 项（subpart 1500）与 S-X 第 14 条 — Release 33-11275 的通行描述 — 属实。
- 外国私人发行人董事与高管 2026-03-18 起适用第 16(a) 条 — 见 s13-sources — 属实。
- 规则 14a-8 提案中经纪商查询期限 20 → 5 个工作日 — https://www.sec.gov/newsroom/press-releases/2026-89-sec-proposes-rescission-shareholder-proposal-rule-reforms-proxy-solicitation-process — 属实。
- 纳斯达克董事会多元化规则 2024-12-11 被撤销 — 见 s13-sources — 属实。

## 地图数据（notes/map-s13.json）
- 11 条规则，stage 全部为 d10，g 为 s13；与已有 map-*.json 无重复 id（map-core 已有 periodic、reg-fd、insider、10b5，未重复收录）。
- year 字段：reg-sk-sx 取 S-X 的 1940；sched-13dg 与 williams-tender 取 1968；sec16a 取 1934；exec-comp 取 1992（第 402 项表格式披露的改版年份，不是最早的薪酬披露要求）。

## 仍不确定的点
- 10-K 引用委托书的 120 天规则、规则 14e-2 的 10 个工作日依据通行知识，未在本轮打开原文。
- 13D 新期限生效日 2024-02-05 来自律所摘要计算，未见 SEC 原文写明该日期。
- 「券商内部截止时间早于发行人公布的最终期限」是行业做法描述，没有对应的规则条文。
- exec-comp 的 year=1992 只代表现行表格式披露的起点。
