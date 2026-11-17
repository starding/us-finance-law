# 用法：python3 gen_panorama.py → 读取 notes/map-*.json（每条一条规则），生成 figs/dmap-panorama.html：
# 合规全景地图。两种视图：「按业务阶段」横轴为 9 个阶段、纵轴为规则来源；「按出台年份」横轴为年份、每行一个阶段。
# 可筛选「2023–2026 年有变化」；点选一条规则查看要求、现状与对应章节。
# 字段：id, name, stage(d01–d09), layer(law/sec/finra/fed/fincen/court/state), year, req, status, changed(bool), g(生成式章节，可空), d(分解式页面)
import json, pathlib

ROOT = pathlib.Path(__file__).parent
STAGES = [("d01", "设立"), ("d02", "获客与沟通"), ("d03", "开户"), ("d04", "入金与托管"), ("d05", "推荐"),
          ("d06", "下单与执行"), ("d07", "成交之后"), ("d08", "持续监控"), ("d09", "退出与事件")]
LAYERS = [("law", "国会成文法"), ("court", "判例"), ("sec", "SEC 规则"), ("fed", "美联储规则"),
          ("finra", "FINRA 规则"), ("fincen", "FinCEN · OFAC"), ("state", "州法")]

def load():
    rules, seen = [], set()
    for p in sorted((ROOT / "notes").glob("map-*.json")):
        for r in json.loads(p.read_text()):
            if r["id"] in seen:
                continue
            seen.add(r["id"]); rules.append(r)
    return rules

def figure(rules):
    data = json.dumps(dict(S=STAGES, L=LAYERS, R=rules), ensure_ascii=False)
    n, c = len(rules), sum(1 for r in rules if r.get("changed"))
    return f'''<figure class="wide">
  <div class="card">
    <div class="figbar"><div><p class="figtitle">合规全景地图：一家线上券商服务一位客户</p><p class="figsub">共 {n} 条规则，其中 {c} 条在 2023–2026 年有变化。切换视图或筛选，点选一条规则查看要求与现状。</p></div></div>
    <div class="pnm-ctl"><div class="pnm-seg" id="pnm-v"><button type="button" data-v="s" class="on">按业务阶段</button><button type="button" data-v="y">按出台年份</button></div>
      <label class="pnm-ck"><input type="checkbox" id="pnm-c"> 只看 2023–2026 年有变化的</label></div>
    <div class="pnm" id="pnm"></div>
    <div class="pnm-d" id="pnm-d" aria-live="polite"></div>
  </div>
</figure>
<style>
body[data-page="d-preface"] .wrap{{max-width:min(1280px,94vw)}}
.pnm-g{{min-width:980px}}
.pnm-ctl{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px;font-size:13px}}
.pnm-seg button{{font:inherit;font-size:12.5px;border:1px solid var(--line);background:transparent;color:var(--muted);padding:4px 12px;cursor:pointer}}
.pnm-seg button:first-child{{border-radius:999px 0 0 999px}}.pnm-seg button:last-child{{border-radius:0 999px 999px 0;margin-left:-1px}}
.pnm-seg button.on{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.pnm-ck{{color:var(--muted)}}.pnm-ck input{{accent-color:var(--accent)}}
.pnm{{overflow-x:auto}}
.pnm-g{{display:grid;min-width:880px;font-size:11.5px}}
.pnm-h{{font-weight:600;font-size:12px;padding:6px 4px;border-bottom:2px solid var(--ink);line-height:1.3}}
.pnm-h a{{color:var(--ink);text-decoration:none}}.pnm-h small{{display:block;color:var(--faint);font-weight:400}}
.pnm-l{{font-size:12px;color:var(--muted);padding:8px 6px 8px 0;border-top:1px solid var(--line)}}
.pnm-c{{border-top:1px solid var(--line);padding:5px 3px;display:flex;flex-direction:column;gap:3px}}
.pnm-r{{font:inherit;font-size:11.5px;text-align:left;cursor:pointer;border:1px solid transparent;background:var(--quote);color:var(--ink);border-radius:6px;padding:4px 6px;line-height:1.3}}
.pnm-r.chg{{background:var(--accent-soft);border-color:var(--accent)}}
.pnm-r.dim{{opacity:.18}}.pnm-r.on{{outline:2px solid var(--ink)}}
.pnm-y{{position:relative;min-width:880px}}
.pnm-yr{{display:grid;grid-template-columns:110px 1fr;border-top:1px solid var(--line);min-height:34px;align-items:center}}
.pnm-yr>span{{font-size:12px;color:var(--muted)}}
.pnm-yt{{position:relative;height:34px}}
.pnm-dot{{position:absolute;top:50%;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;border:2px solid var(--ink);background:var(--card);cursor:pointer;padding:0}}
.pnm-dot.chg{{background:var(--accent);border-color:var(--accent)}}.pnm-dot.dim{{opacity:.15}}.pnm-dot.on{{box-shadow:0 0 0 4px var(--accent-soft)}}
.pnm-ax{{display:grid;grid-template-columns:110px 1fr;border-top:1px solid var(--line)}}.pnm-ax div{{position:relative;height:20px}}
.pnm-ax i{{position:absolute;top:3px;transform:translateX(-50%);font-style:normal;font-size:11px;color:var(--faint)}}
.pnm-d{{margin-top:12px;background:var(--quote);border-radius:10px;padding:12px 14px;font-size:13.5px;line-height:1.6;min-height:6em}}
.pnm-d b{{font-size:14.5px}}.pnm-d em{{font-style:normal;color:var(--muted);font-size:12.5px;display:block;margin-top:4px}}
.pnm-d .st{{display:block;margin-top:6px;font-size:13px}}.pnm-d a{{color:var(--accent);margin-right:12px}}
</style>
<script>
(function(){{
  const D={data},S=D.S,L=D.L,R=D.R,box=document.getElementById('pnm'),det=document.getElementById('pnm-d');
  const sn=Object.fromEntries(S),ln=Object.fromEntries(L);let view='s',only=false,cur=-1;
  const lnk=(f,t)=>'<a data-f="'+f+'">'+t+'</a>';
  function show(i){{cur=i;const r=R[i];
    det.innerHTML='<b>'+r.name+'</b><br>'+r.req+'<span class="st">现状：'+r.status+'</span><em>'+sn[r.stage]+' · '+ln[r.layer]+' · '+r.year+' 年</em>'+(r.d?lnk(r.d,'分解式：'+sn[r.stage]+' →'):'')+(r.g?lnk(r.g,'生成式：第 '+(+r.g.slice(1))+' 章 →'):'');
    det.querySelectorAll('a[data-f]').forEach(a=>a.setAttribute('href',a.dataset.f+'.'+'html'));
    box.querySelectorAll('[data-i]').forEach(e=>e.classList.toggle('on',+e.dataset.i===i));}}
  function drawS(){{let h='<div class="pnm-g" style="grid-template-columns:96px repeat('+S.length+',1fr)"><div class="pnm-h"></div>';
    S.forEach(s=>h+='<div class="pnm-h">'+lnk(s[0],s[1])+'<small>'+R.filter(r=>r.stage===s[0]).length+' 条</small></div>');
    L.forEach(l=>{{if(!R.some(r=>r.layer===l[0]))return;h+='<div class="pnm-l">'+l[1]+'</div>';
      S.forEach(s=>{{h+='<div class="pnm-c">';R.forEach((r,i)=>{{if(r.stage===s[0]&&r.layer===l[0])h+='<button type="button" class="pnm-r'+(r.changed?' chg':'')+(only&&!r.changed?' dim':'')+'" data-i="'+i+'">'+r.name+'</button>';}});h+='</div>';}});}});
    box.innerHTML=h+'</div>';}}
  function drawY(){{const Y0=1905,Y1=2030,x=y=>((y-Y0)/(Y1-Y0)*100).toFixed(2)+'%';let h='<div class="pnm-y">';
    S.forEach(s=>{{h+='<div class="pnm-yr"><span>'+s[1]+'</span><div class="pnm-yt">';R.forEach((r,i)=>{{if(r.stage===s[0])h+='<button type="button" class="pnm-dot'+(r.changed?' chg':'')+(only&&!r.changed?' dim':'')+'" style="left:'+x(r.year)+'" data-i="'+i+'" title="'+r.name+'（'+r.year+'）"></button>';}});h+='</div></div>';}});
    h+='<div class="pnm-ax"><div></div><div>'+[1910,1930,1950,1970,1990,2010,2026].map(y=>'<i style="left:'+x(y)+'">'+y+'</i>').join('')+'</div></div></div>';box.innerHTML=h;}}
  function draw(){{view==='s'?drawS():drawY();box.querySelectorAll('a[data-f]').forEach(a=>a.setAttribute('href',a.dataset.f+'.'+'html'));
    box.querySelectorAll('[data-i]').forEach(e=>e.addEventListener('click',()=>show(+e.dataset.i)));if(cur>=0)show(cur);}}
  document.querySelectorAll('#pnm-v button').forEach(b=>b.addEventListener('click',()=>{{view=b.dataset.v;document.querySelectorAll('#pnm-v button').forEach(x=>x.classList.toggle('on',x===b));draw();}}));
  document.getElementById('pnm-c').addEventListener('change',e=>{{only=e.target.checked;draw();}});
  draw();if(R.length)show(R.findIndex(r=>r.changed)>=0?R.findIndex(r=>r.changed):0);
}})();
</script>
'''

if __name__ == "__main__":
    rules = load()
    (ROOT / "figs" / "dmap-panorama.html").write_text(figure(rules))
    print("全景地图：", len(rules), "条规则，", sum(1 for r in rules if r.get("changed")), "条有变化")
