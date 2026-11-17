# 用法：python3 gen_map.py → 从 chapters/ 中证券篇各章（s01–s12）的规则卡收集名称、一句话表述与出台年份，
# 生成 figs/smap-rules.html：横轴为年份，每行一个问题（章），每张规则卡一个点，点选查看卡片摘要。
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent

def collect():
    rows = []
    for p in sorted((ROOT / "chapters").glob("*.md")):
        s = p.read_text()
        m = re.search(r"^file:\s*(s\d\d)\s*$", s, re.M)
        if not m:
            continue
        f = m[1]
        title = re.search(r"^title:\s*(.+)$", s, re.M)[1].strip()
        body = s.split("<!-- body -->", 1)[-1]
        cards = []
        for kind, name, inner in re.findall(r"^:::(原理|重跑) (.+?)\n(.*?)\n:::$", body, re.M | re.S):
            ls = [x.strip() for x in inner.split("\n") if x.strip()]
            fields = dict(x.split("：", 1) for x in ls[1:] if "：" in x)
            years = [int(y) for y in re.findall(r"(1[89]\d\d|20[0-2]\d)", fields.get("提出", ""))]
            if not years:
                continue
            cards.append(dict(name=name.strip(), text=ls[0], year=min(years), years=sorted(set(years)),
                              by=fields.get("提出", ""), kind=kind, ask=fields.get("约束", "")))
        rows.append(dict(f=f, no=int(f[1:]), title=title, cards=cards))
    return rows

def figure(rows):
    data = json.dumps(rows, ensure_ascii=False)
    n = sum(len(r["cards"]) for r in rows)
    return f'''<figure>
  <div class="card">
    <div class="figbar"><div><p class="figtitle">证券篇的规则地图</p><p class="figsub">每行一个问题，每个点是一张规则卡，横轴为最早出台的年份；空心点为第 12 章重新检验的规则。共 {n} 张卡片。点选一个点查看摘要。</p></div></div>
    <div class="rmp" id="rmp"></div>
    <div class="rmp-d" id="rmp-d" aria-live="polite"></div>
  </div>
</figure>
<style>
.rmp{{position:relative;font-size:12.5px}}
.rmp-row{{display:grid;grid-template-columns:200px 1fr;align-items:center;min-height:30px;border-top:1px solid var(--line)}}
.rmp-row a{{color:var(--ink);text-decoration:none;padding:4px 8px 4px 0;line-height:1.3}}
.rmp-row a span{{color:var(--faint);margin-right:6px}}
.rmp-track{{position:relative;height:30px}}
.rmp-dot{{position:absolute;top:50%;width:13px;height:13px;margin:-6.5px 0 0 -6.5px;border-radius:50%;background:var(--accent);border:2px solid var(--accent);cursor:pointer;padding:0}}
.rmp-dot.rr{{background:var(--card)}}
.rmp-dot.on{{box-shadow:0 0 0 4px var(--accent-soft)}}
.rmp-ax{{display:grid;grid-template-columns:200px 1fr;border-top:1px solid var(--line)}}
.rmp-ax div{{position:relative;height:22px}}
.rmp-ax span{{position:absolute;top:4px;transform:translateX(-50%);color:var(--faint);font-size:11.5px}}
.rmp-d{{margin-top:12px;background:var(--quote);border-radius:10px;padding:12px 14px;font-size:13.5px;line-height:1.6;min-height:4.5em}}
.rmp-d b{{display:block;font-size:14px}}.rmp-d em{{font-style:normal;color:var(--muted);font-size:12.5px}}
@media (max-width:640px){{.rmp-row,.rmp-ax{{grid-template-columns:110px 1fr}}}}
</style>
<script>
(function(){{
  const R={data},Y0=1905,Y1=2030,x=y=>((y-Y0)/(Y1-Y0)*100).toFixed(2)+'%';
  const g=document.getElementById('rmp'),d=document.getElementById('rmp-d');
  let h='';const all=[];
  R.forEach(r=>{{h+=`<div class="rmp-row"><a data-f="${{r.f}}"><span>${{r.no}}</span>${{r.title}}</a><div class="rmp-track">`;
    r.cards.forEach((c,i)=>{{all.push([r,c]);h+=`<button type="button" class="rmp-dot${{c.kind==='重跑'?' rr':''}}" style="left:${{x(c.year)}}" data-k="${{all.length-1}}" title="${{c.name}}（${{c.year}}）"></button>`;}});
    h+='</div></div>';}});
  h+='<div class="rmp-ax"><div></div><div>'+[1910,1930,1950,1970,1990,2010,2026].map(y=>`<span style="left:${{x(y)}}">${{y}}</span>`).join('')+'</div></div>';
  g.innerHTML=h;g.querySelectorAll('a[data-f]').forEach(a=>a.setAttribute('href',a.dataset.f+'.'+'html'));const bs=[...g.querySelectorAll('.rmp-dot')];
  function set(k){{bs.forEach(b=>b.classList.toggle('on',+b.dataset.k===k));const [r,c]=all[k];
    d.innerHTML=`<b>${{c.name}}</b>${{c.text}}<br><em>第 ${{r.no}} 章 · 回应：${{c.ask}} · 出台：${{c.by}}</em>`;}}
  bs.forEach(b=>b.addEventListener('click',()=>set(+b.dataset.k)));if(all.length)set(0);
}})();
</script>
'''

if __name__ == "__main__":
    rows = collect()
    (ROOT / "figs" / "smap-rules.html").write_text(figure(rows))
    print("规则卡：", sum(len(r["cards"]) for r in rows), "张，来自", len(rows), "章")
