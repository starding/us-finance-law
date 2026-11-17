# 用法：python3 gen_panorama.py → 读取 notes/map-*.json（每条一条规则），生成 figs/dmap-panorama.html：
# 合规全景地图。两种视图：「按业务阶段」横轴为 9 个阶段、纵轴为规则来源；「按出台年份」横轴为年份、每行一个阶段。
# 可筛选「2023–2026 年有变化」；点选一条规则查看要求、现状与对应章节。
# 字段：id, name, stage(d01–d09), layer(law/sec/finra/fed/fincen/court/state), year, req, status, changed(bool), g(生成式章节，可空), d(分解式页面)
import json, pathlib, re
from gen_history import ERAS

ROOT = pathlib.Path(__file__).parent
STAGES = [("d01", "设立"), ("d02", "获客与沟通"), ("d03", "开户"), ("d04", "入金与托管"), ("d05", "推荐"),
          ("d06", "下单与执行"), ("d07", "成交之后"), ("d08", "持续监控"), ("d09", "退出与事件"), ("d10", "发行人：持续义务")]
LAYERS = [("law", "国会成文法"), ("court", "判例"), ("sec", "SEC 规则"), ("fed", "美联储规则"),
          ("finra", "FINRA 规则"), ("exch", "交易所与清算机构规则"), ("fincen", "FinCEN · OFAC"), ("state", "州法")]
# 监管对象与各自的核心环节（横轴第一层与第二层）
OBJECTS = [
    ("issuer", "发行人", ["发行注册", "持续披露", "治理与内部人", "收购与控制", "跨境发行人"]),
    ("broker", "经纪自营商", [n for k, n in STAGES[:9]]),
    ("adviser", "投资顾问", ["注册", "受托义务", "营销", "托管"]),
    ("fund", "基金与 ETP", ["结构与估值", "披露与销售", "衍生品与杠杆"]),
    ("venue", "交易场所", ["注册与自律", "行情与 NBBO", "交易规则"]),
    ("infra", "清算、结算与报告", ["清算与结算", "交易报告与审计追踪", "过户与持有人记录"]),
    ("investor", "投资者与市场行为", ["大额持股与内部人", "卖空", "操纵与内幕交易"]),
    ("all", "执法与救济", ["执法", "诉讼与仲裁", "吹哨人"]),
]


def chno():
    """章节 id → 显示的章号，取自 build.py 的目录"""
    import build
    return {f: int(re.search(r"\d+", no)[0]) for f, no, t, p in build.TOC if f.startswith("s") and re.search(r"\d+", no)}

OBJ_PAGE = {"issuer": "d10", "adviser": "o-adviser", "fund": "o-fund", "venue": "o-venue", "infra": "o-infra", "investor": "o-investor", "all": "o-all"}
PAGE_NAME = dict(STAGES) | {"o-adviser": "投资顾问", "o-fund": "基金与 ETP", "o-venue": "交易场所", "o-infra": "清算、结算与报告", "o-investor": "投资者与市场行为", "o-all": "执法与救济"}

def tag(r, ov):
    """给规则标上监管对象与环节：优先用 notes/objects.json，其次按 stage 推断"""
    if r["id"] in ov:
        t = ov[r["id"]]; r["obj"], r["link"] = t[0], t[1]
        if len(t) > 2: r["layer"] = t[2]
    elif r.get("obj") and r.get("link"):
        pass
    elif r["stage"] == "d10":
        r["obj"], r["link"] = "issuer", r.get("link") or "持续披露"
    else:
        r["obj"], r["link"] = "broker", dict(STAGES)[r["stage"]]
    if r["obj"] in OBJ_PAGE:
        r["d"] = OBJ_PAGE[r["obj"]]
    return r

def load():
    ov = {k: v for k, v in json.loads((ROOT / "notes" / "objects.json").read_text()).items() if not k.startswith("_")}
    rules, seen = [], set()
    for p in sorted((ROOT / "notes").glob("map-*.json")):
        for r in json.loads(p.read_text()):
            if r["id"] in seen:
                continue
            seen.add(r["id"]); rules.append(tag(r, ov))
    return rules

def figure(rules):
    data = json.dumps(dict(O=OBJECTS, L=LAYERS, R=rules, C=chno(), S=STAGES, P=PAGE_NAME, E=ERAS), ensure_ascii=False)
    n, c = len(rules), sum(1 for r in rules if r.get("changed"))
    return f"""<figure>
  <div class="card">
    <div class="figbar"><div><p class="figtitle">合规全景地图：谁定的规则 × 管的是谁、管哪个环节</p><p class="figsub">纵轴是规则的制定主体，横轴是监管对象；点对象名展开到它的核心环节。共 {n} 条规则，其中 {c} 条在 2023–2026 年有变化。</p></div></div>
    <div class="pnm-ctl"><div class="pnm-seg" id="pnm-v"><button type="button" data-v="o" class="on">按监管对象</button><button type="button" data-v="y">按出台年份</button></div>
      <span class="pnm-crumb" id="pnm-b"></span>
      <label class="pnm-ck"><input type="checkbox" id="pnm-c"> 只看 2023–2026 年有变化的</label></div>
    <div class="pnm" id="pnm"></div>
    <div class="pnm-d" id="pnm-d" aria-live="polite"></div>
  </div>
</figure>
<style>

.lyx-wrap{{overflow-x:auto}}
.lyx-in{{position:relative;width:calc(2200px + 130px)}}
.lyx-era{{display:grid;grid-template-columns:repeat(7,1fr);margin-left:130px}}
.lyx-era div{{border-left:1px solid var(--line);padding:4px 6px}}.lyx-era b{{display:block;font-size:12px}}.lyx-era small{{font-size:11px;color:var(--faint)}}
.lyx-row{{display:grid;grid-template-columns:130px 1fr;border-top:1px solid var(--line)}}
.lyx-row>span{{font-size:12px;color:var(--muted);padding:8px 6px 0 0}}
.lyx-tr{{position:relative}}.lyx-tr i{{position:absolute;top:0;bottom:0;border-left:1px solid var(--line);opacity:.6}}
.lyx-c{{position:absolute;font:inherit;font-size:11.5px;white-space:nowrap;cursor:pointer;border:1px solid transparent;background:var(--quote);color:var(--ink);border-radius:6px;padding:2px 7px;line-height:1.5}}
.lyx-c.chg{{background:var(--accent-soft);border-color:var(--accent)}}.lyx-c.dim{{opacity:.15}}.lyx-c.on{{outline:2px solid var(--ink)}}.lyx-c.hl{{outline:2px solid var(--accent)}}
body[data-page="d-preface"] .wrap{{max-width:min(1360px,95vw)}}
.pnm-ctl{{display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px;font-size:13px}}
.pnm-seg button{{font:inherit;font-size:12.5px;border:1px solid var(--line);background:transparent;color:var(--muted);padding:4px 12px;cursor:pointer}}
.pnm-seg button:first-child{{border-radius:999px 0 0 999px}}.pnm-seg button:last-child{{border-radius:0 999px 999px 0;margin-left:-1px}}
.pnm-seg button.on{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.pnm-crumb{{flex:1;color:var(--muted)}}.pnm-crumb button{{font:inherit;font-size:12.5px;border:0;background:none;color:var(--accent);cursor:pointer;padding:0}}
.pnm-ck{{color:var(--muted)}}.pnm-ck input{{accent-color:var(--accent)}}
.pnm{{overflow-x:auto}}
.pnm-g{{display:grid;min-width:1040px;font-size:11.5px}}
.pnm-h{{font-size:12px;padding:6px 4px;border-bottom:2px solid var(--ink);line-height:1.3}}
.pnm-h button{{font:inherit;font-weight:600;font-size:12.5px;border:0;background:none;color:var(--ink);cursor:pointer;padding:0;text-align:left}}
.pnm-h button:hover{{color:var(--accent)}}.pnm-h a{{color:var(--ink);font-weight:600;text-decoration:none}}
.pnm-h small{{display:block;color:var(--faint);font-weight:400}}
.pnm-l{{font-size:12px;color:var(--muted);padding:8px 6px 8px 0;border-top:1px solid var(--line)}}
.pnm-c{{border-top:1px solid var(--line);padding:5px 3px;display:flex;flex-direction:column;gap:3px}}
.pnm-r{{font:inherit;font-size:11.5px;text-align:left;cursor:pointer;border:1px solid transparent;background:var(--quote);color:var(--ink);border-radius:6px;padding:4px 6px;line-height:1.3}}
.pnm-more{{font:inherit;font-size:11.5px;border:1px dashed var(--line);background:none;color:var(--muted);border-radius:6px;padding:3px 6px;cursor:pointer;text-align:left}}
.pnm-r.chg{{background:var(--accent-soft);border-color:var(--accent)}}.pnm-r.dim{{opacity:.15}}.pnm-r.on{{outline:2px solid var(--ink)}}
.pnm-yr{{display:grid;grid-template-columns:130px 1fr;border-top:1px solid var(--line);min-height:34px;align-items:center;min-width:900px}}
.pnm-yr>span{{font-size:12px;color:var(--muted)}}.pnm-yt{{position:relative}}
.pnm-dot{{position:absolute;width:12px;height:12px;margin-left:-6px;border-radius:50%;border:2px solid var(--ink);background:var(--card);cursor:pointer;padding:0}}
.pnm-dot.chg{{background:var(--accent);border-color:var(--accent)}}.pnm-dot.dim{{opacity:.15}}.pnm-dot.on{{box-shadow:0 0 0 4px var(--accent-soft)}}
.pnm-ax{{display:grid;grid-template-columns:130px 1fr;border-top:1px solid var(--line);min-width:900px}}.pnm-ax div{{position:relative;height:20px}}
.pnm-ax i{{position:absolute;top:3px;transform:translateX(-50%);font-style:normal;font-size:11px;color:var(--faint)}}
.pnm-d{{margin-top:12px;background:var(--quote);border-radius:10px;padding:12px 14px;font-size:13.5px;line-height:1.6;min-height:6em}}
.pnm-d b{{font-size:14.5px}}.pnm-d em{{font-style:normal;color:var(--muted);font-size:12.5px;display:block;margin-top:4px}}
.pnm-d .st{{display:block;margin-top:6px;font-size:13px}}.pnm-d a{{color:var(--accent);margin-right:12px}}
</style>
<script>
(function(){{
  const D={data},O=D.O,L=D.L,R=D.R,C=D.C,box=document.getElementById('pnm'),det=document.getElementById('pnm-d'),crumb=document.getElementById('pnm-b');
  const on=Object.fromEntries(O.map(o=>[o[0],o[1]])),ln=Object.fromEntries(L),sn=D.P;
  let view='o',obj=null,only=false,cur=-1;
  const ERA=D.E,NE=ERA.length,W=2200;
  const EW=ERA.map(e=>Math.max(1,Math.sqrt(D.R.filter(r=>r.year>=e[0]&&r.year<=e[1]).length))),ES=EW.reduce((a,b)=>a+b,0),EC=EW.map((w,k)=>EW.slice(0,k).reduce((a,b)=>a+b,0)/ES);
  const pos=y=>{{let k=ERA.findIndex(e=>y>=e[0]&&y<=e[1]);if(k<0)k=y<ERA[0][0]?0:NE-1;const e=ERA[k],f=(Math.min(Math.max(y,e[0]),e[1])-e[0]+0.5)/(e[1]-e[0]+1);return EC[k]+f*EW[k]/ES;}};
  const short=n=>{{let s=n.length>16&&n.indexOf('（')>3?n.slice(0,n.indexOf('（')):n;return s.length>18?s.slice(0,17)+'…':s;}};
  function lane(items,cls){{const ends=[];let h='';items.sort((a,b)=>a[0].year-b[0].year).forEach(([r,i])=>{{const t=short(r.name),w=t.length*12.2+16,x=pos(r.year)*W;let k=0;while(ends[k]!==undefined&&x<ends[k]+4)k++;ends[k]=x+w;
      h+='<button type="button" class="'+cls+(r.changed?' chg':'')+'" data-i="'+i+'" style="left:'+x.toFixed(0)+'px;top:'+(6+k*25)+'px" title="'+r.name+'（'+r.year+'）">'+t+'</button>';}});
    return [h,10+ends.length*25];}}
  const eraHead=()=>'<div class="lyx-era" style="width:'+W+'px;grid-template-columns:'+EW.map(w=>w+'fr').join(' ')+'">'+ERA.map(e=>'<div><b>'+e[2]+'</b><small>'+e[0]+'–'+e[1]+'</small></div>').join('')+'</div>';
  const eraGrid=()=>ERA.map((e,k)=>'<i style="left:'+(EC[k]*W)+'px"></i>').join('');

  const lnk=(f,t)=>'<a data-f="'+f+'">'+t+'</a>';
  const fix=el=>el.querySelectorAll('a[data-f]').forEach(a=>a.setAttribute('href',a.dataset.f+'.'+'html'));
  const chip=(r,i)=>'<button type="button" class="pnm-r'+(r.changed?' chg':'')+(only&&!r.changed?' dim':'')+'" data-i="'+i+'">'+r.name+'</button>';
  function show(i){{cur=i;const r=R[i];
    det.innerHTML='<b>'+r.name+'</b><br>'+r.req+'<span class="st">现状：'+r.status+'</span><em>'+on[r.obj]+' · '+r.link+' · '+ln[r.layer]+' · '+r.year+' 年</em>'+(r.d?lnk(r.d,'分解式：'+(sn[r.d]||'页面')+' →'):'')+(r.g?lnk(r.g,'生成式：第 '+(C[r.g]||'')+' 章 →'):'');
    fix(det);box.querySelectorAll('[data-i]').forEach(e=>e.classList.toggle('on',+e.dataset.i===i));}}
  function grid(cols,colOf,head,lim){{lim=lim||999;const used=L.filter(l=>R.some(r=>r.layer===l[0]&&cols.some(c=>colOf(r)===c[0])));
    let h='<div class="pnm-g" style="grid-template-columns:110px repeat('+cols.length+',minmax(108px,1fr))"><div class="pnm-h"></div>'+cols.map(head).join('');
    used.forEach(l=>{{h+='<div class="pnm-l">'+l[1]+'</div>';cols.forEach(c=>{{h+='<div class="pnm-c">';const rs=R.map((r,i)=>[r,i]).filter(([r])=>r.layer===l[0]&&colOf(r)===c[0]).sort((a,b)=>(b[0].changed?1:0)-(a[0].changed?1:0));
      rs.slice(0,lim).forEach(([r,i])=>h+=chip(r,i));if(rs.length>lim)h+='<button type="button" class="pnm-more" data-o="'+c[0]+'">＋'+(rs.length-lim)+' 条</button>';h+='</div>';}});}});
    return h+'</div>';}}
  function draw(){{
    if(view==='y'){{crumb.innerHTML='规则名按最早出台的年份排列；规则越多的时期越宽，可横向滚动';let h='<div class="lyx-in">'+eraHead();
      O.forEach(o=>{{const it=R.map((r,i)=>[r,i]).filter(([r])=>r.obj===o[0]);if(!it.length)return;const [lh,ht]=lane(it,'lyx-c');
        h+='<div class="lyx-row"><span>'+o[1]+'</span><div class="lyx-tr" style="height:'+ht+'px">'+eraGrid()+lh+'</div></div>';}});
      box.innerHTML=h+'</div>';if(only)box.querySelectorAll('.lyx-c:not(.chg)').forEach(e=>e.classList.add('dim'));}}
    else if(!obj){{crumb.innerHTML='点对象名，展开到它的核心环节';
      box.innerHTML=grid(O.map(o=>[o[0],o[1]]),r=>r.obj,c=>'<div class="pnm-h"><button type="button" data-o="'+c[0]+'">'+c[1]+' ›</button><small>'+R.filter(r=>r.obj===c[0]).length+' 条</small></div>',5);}}
    else{{const o=O.find(x=>x[0]===obj);crumb.innerHTML='<button type="button" data-back>← 全部监管对象</button>　'+o[1]+'的核心环节';
      box.innerHTML=grid(o[2].map(n=>[n,n]),r=>r.obj===obj?r.link:null,c=>{{const st=obj==='broker'?D.S.find(s=>s[1]===c[1]):null;return '<div class="pnm-h">'+(st?lnk(st[0],c[1]):c[1])+'<small>'+R.filter(r=>r.obj===obj&&r.link===c[0]).length+' 条</small></div>';}});}}
    fix(box);fix(crumb);
    box.querySelectorAll('[data-i]').forEach(e=>e.addEventListener('click',()=>show(+e.dataset.i)));
    box.querySelectorAll('[data-o]').forEach(e=>e.addEventListener('click',()=>{{obj=e.dataset.o;draw();}}));
    crumb.querySelectorAll('[data-back]').forEach(e=>e.addEventListener('click',()=>{{obj=null;draw();}}));
    if(cur>=0)show(cur);}}
  document.querySelectorAll('#pnm-v button').forEach(b=>b.addEventListener('click',()=>{{view=b.dataset.v;document.querySelectorAll('#pnm-v button').forEach(x=>x.classList.toggle('on',x===b));draw();}}));
  document.getElementById('pnm-c').addEventListener('change',e=>{{only=e.target.checked;draw();}});
  if(location.hash==='#years'){{view='y';document.querySelectorAll('#pnm-v button').forEach(x=>x.classList.toggle('on',x.dataset.v==='y'));}}
  draw();const k=R.findIndex(r=>r.changed);if(R.length)show(k>=0?k:0);
}})();
</script>
"""

if __name__ == "__main__":
    rules = load()
    (ROOT / "figs" / "dmap-panorama.html").write_text(figure(rules))
    print("全景地图：", len(rules), "条规则，", sum(1 for r in rules if r.get("changed")), "条有变化")
