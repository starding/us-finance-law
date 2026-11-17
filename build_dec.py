# 用法：python3 build_dec.py（由 build.py 自动调用）→ 由 dec/*.md 生成分解式页面 site/d-*.html（图共用 figs/）。
# 分解式：沿着一家线上券商服务一位客户的时间轴，把合规义务按业务阶段拆开；全景地图把各阶段的规则按来源与年份排在一张图上。
import pathlib
import build

TOC = [
    ("d-preface", "导读", "合规全景地图", None),
    ("d-part", "分解式", "沿着业务的时间轴", "part"),
    ("d01", "阶段 1", "设立：成为一家经纪自营商", 1),
    ("d02", "阶段 2", "获客与沟通", 1),
    ("d03", "阶段 3", "开户", 1),
    ("d04", "阶段 4", "入金与托管", 1),
    ("d05", "阶段 5", "推荐", 1),
    ("d06", "阶段 6", "下单与执行", 1),
    ("d07", "阶段 7", "成交之后：结算、确认与报告", 1),
    ("d08", "阶段 8", "持续监控与监督", 1),
    ("d09", "阶段 9", "退出与事件处置", 1),
    ("method", "附录", "本书的写法", "app"),
]

def main():
    pages = sorted((build.SRC / "dec").glob("*.md"))
    done = {build.parse(p)[0]["file"] for p in pages} | {"method"}
    keep = (build.TOC, build.DONE, build.WRITTEN, build.VIEW)
    build.TOC, build.DONE = TOC, done
    build.WRITTEN = [t for t in TOC if t[0] in done]
    build.VIEW = "d"
    for old in build.OUT.glob("d-*.html"):
        old.unlink()
    for old in build.OUT.glob("d0*.html"):
        old.unlink()
    built = [build.build_page(p) for p in pages]
    build.TOC, build.DONE, build.WRITTEN, build.VIEW = keep
    print(f"[{build.LANG}] 分解式已生成：", ", ".join(built))
