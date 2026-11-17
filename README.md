# 美国金融业法律研究：规则从何而来

一本关于美国金融业法律规则的交互式网页书。第一篇为证券篇。

**在线阅读：** 见仓库 About 栏中的 GitHub Pages 链接。

## 两种读法

- **分解式**：以合规全景地图为导读。纵轴是规则的制定主体（国会、判例、SEC、美联储、FINRA、交易所与清算机构、FinCEN/OFAC、州），横轴是八类监管对象（发行人、经纪自营商、投资顾问、基金与 ETP、交易场所、清算结算与报告、投资者与市场行为、执法与救济）；经纪自营商按服务一位客户的时间轴展开为九个环节。
- **生成式**：以历史时间轴地图为导读。从一个没有证券法的市场出发，每一章只引入一个新问题，推演规则为什么出现；共十七章，最后一章把「推荐来自 AI」作为新参数重跑一遍。

## 构建

```bash
python3 gen_map.py && python3 gen_panorama.py && python3 gen_history.py && python3 gen_objects.py
python3 build.py   # 由 chapters/、dec/、figs/ 生成 site/
```

- 规则数据：`notes/map-*.json`，监管对象标注 `notes/objects.json`。
- 核实清单：`notes/*-sources.md`，逐条列出说法、来源与结论，以及仍不确定的事项。

## 署名

- 立意与结构：兴华 XingHua
- 正文与交互图：Claude 撰写，兴华 XingHua 指导与修订
- 事实核实：Claude
- 审校：兴华 XingHua

资料截至 2026 年 11 月。本书讨论法律规则的来由与结构，不构成法律意见。
