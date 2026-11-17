# 用法：python3 gen_objects.py → 为没有手写页面的监管对象，由全景地图数据生成分解式页面 dec/2X-o-*.md：
# 按核心环节分节，每节一张规则表（规则、要求、制定主体、现状、详见）。手写页面（经纪自营商 d01–d09、发行人 d10）不在此生成。
import pathlib, re
import gen_panorama as gp

ROOT = pathlib.Path(__file__).parent
INTRO = {
    "adviser": "投资顾问替客户管理资产或提供个性化的投资建议，按 1940 年《投资顾问法》向 SEC 或州注册。与经纪商不同，顾问对客户负有受托义务，营销、托管与利益冲突都有专门的规则。",
    "fund": "共同基金、ETF 与其他交易所交易产品把许多投资者的钱集中起来投资，受 1940 年《投资公司法》的结构性约束：独立董事、杠杆限制、每日估值与赎回；券商销售这些产品时，还要遵守披露与适当性要求。",
    "venue": "交易所与另类交易系统把买卖双方的报价集中起来撮合成交。交易所须向 SEC 注册并承担自律职能；行情由统一的证券信息处理器汇总为全国最优买卖报价；价格带、熔断与报价单位等交易规则由交易场所与 SEC 共同制定。",
    "infra": "成交之后，清算机构、托管机构与过户代理完成结算与登记，交易数据报送给监管机构的合并审计追踪。这些机构不直接面对零售客户，但决定了结算周期、报告时限与持有人记录。",
    "investor": "投资者自身也是监管对象：持股超过一定比例要披露，公司内部人的交易要报告，卖空要遵守借券与报告规则，任何人都不得操纵市场或利用内幕信息交易。",
    "all": "规则被违反之后，由 SEC、FINRA 与司法部追究，投资者可以通过诉讼或仲裁求偿，吹哨人可以获得奖励。这些机制适用于前面所有的监管对象。",
}
LN = dict(gp.LAYERS)

def page(o, k, rules):
    key, name, links = o
    rs = [r for r in rules if r["obj"] == key]
    out = [f"---\nfile: {gp.OBJ_PAGE[key]}\nkind: chapter\nno: 对象\ntitle: {name}\nsubtitle: 核心环节与规则\npart: 分解式\nasof: 2026-11\ndesc: 《美国金融业法律研究》分解式：{name}这一监管对象的核心环节，以及每个环节适用的规则、制定主体与截至 2026 年 11 月的状态\n---\n",
           "最近更新：2026-11-17\n\n| 版本 | 日期 | 内容 |\n|---|---|---|\n| v0.1 | 2026-11-17 | 由合规全景地图的数据生成 |\n\n<!-- body -->\n",
           f"> {INTRO[key]}\n",
           f"本页共 {len(rs)} 条规则，其中 {sum(1 for r in rs if r.get('changed'))} 条在 2023–2026 年有变化。规则的来由见「详见」一列链接的生成式章节；全部规则的分布见[合规全景地图](d-preface.html)。\n"]
    cn = "一二三四五六七八九十"
    n = 0
    for l in links:
        lr = sorted([r for r in rs if r["link"] == l], key=lambda r: r["year"])
        if not lr:
            continue
        out.append(f"## {cn[n]}、{l}\n"); n += 1
        out.append("| 规则 | 要求 | 制定主体 | 现状（截至 2026 年 11 月） | 详见 |\n|---|---|---|---|---|")
        for r in lr:
            see = f"[第 {gp.chno().get(r['g'], '')} 章]({r['g']}.html)" if r.get("g") else "—"
            mark = "（有变化）" if r.get("changed") else ""
            out.append(f"| {r['name']}{mark} | {r['req']} | {LN[r['layer']]} | {r['status']} | {see} |")
        out.append("")
    (ROOT / "dec" / f"2{k}-{gp.OBJ_PAGE[key]}-{name}.md").write_text("\n".join(out) + "\n")
    return gp.OBJ_PAGE[key]

if __name__ == "__main__":
    rules = gp.load()
    for old in (ROOT / "dec").glob("2?-o-*.md"):
        old.unlink()
    made = [page(o, k, rules) for k, o in enumerate(gp.OBJECTS) if o[0] in INTRO]
    print("对象页：", ", ".join(made))
