# 用法：python3 gen_history.py → 读取 notes/map-*.json 的规则与本文件中的事件，生成 figs/hmap-history.html：
# 历史时间轴地图。横轴为分段的年份（每个时期等宽，时期内按年份线性），最上一行为引发立法的事件，其下按规则来源分行；
# 点选事件查看它引出的规则，点选规则查看要求、现状与对应章节。
import json, pathlib, re

ROOT = pathlib.Path(__file__).parent

ERAS = [  # (起, 止, 名称, 一句话)
    (1905, 1932, "州法时代", "各州以蓝天法逐个审查发行，跨州推销管不到"),
    (1933, 1940, "新政立法", "崩盘之后七年，联邦证券法的主干成形"),
    (1941, 1969, "判例与自律", "法院与 SEC 划定边界，NASD 自律监管成熟"),
    (1970, 1989, "危机与重建", "经纪商倒闭催生 SIPC 与客户资产保护，固定佣金取消"),
    (1990, 2007, "电子化与丑闻", "电子交易、市场碎片化与公司丑闻，规则在框架内修补"),
    (2008, 2019, "金融危机之后", "危机、闪电崩盘与零售投资者保护"),
    (2020, 2026, "零售化、加密与 AI", "零佣金与线上券商、加密资产与 AI，规则加速调整"),
]

EVENTS = [  # (年份, 名称, 说明, 引出的规则 id)
    (1911, "第一部蓝天法", "州银行专员多利推动通过，此后除内华达州外各州相继立法", ["blue-sky"]),
    (1929, "股市崩盘", "1929 年 10 月道琼斯指数暴跌，此后三年大萧条；低保证金交易放大了下跌", ["sec-33", "reg-t", "sea-15a"]),
    (1932, "佩科拉听证", "参议院银行委员会调查（1932–1934），揭示发行中的误导与利益冲突", ["sec-33", "manipulation"]),
    (1968, "文书危机", "1968–1970 年成交量激增，经纪商后台处理不及，多家经纪商倒闭或被合并", ["sipa", "customer-protection", "net-capital"]),
    (1975, "取消固定佣金", "1975 年 5 月 1 日起经纪佣金可以协商；同年《证券法修正案》要求建立全国市场体系", ["reg-nms"]),
    (1987, "黑色星期一", "1987 年 10 月 19 日道琼斯指数单日下跌 22.6%，此后引入全市场熔断", ["mwcb"]),
    (2001, "安然与 9·11", "安然 2001 年 12 月申请破产；9·11 之后通过《爱国者法》，强化反洗钱与客户身份识别", ["cip", "aml-program"]),
    (2008, "金融危机", "2008 年 9 月雷曼兄弟破产；12 月麦道夫骗局曝光，SIPC 主持清算", ["sipc-liq"]),
    (2010, "闪电崩盘", "2010 年 5 月 6 日美股在数分钟内暴跌又反弹，此后推出涨跌停价格带与市场准入风险控制", ["luld", "market-access"]),
    (2021, "GameStop", "2021 年 1 月散户集中买入与券商限制交易，引发对订单流付费与执行质量的关注", ["rule-605"]),
    (2022, "FTX 倒闭", "2022 年 11 月加密交易平台 FTX 申请破产，加剧对加密资产托管与分类的讨论", ["howey"]),
]

LAYERS = [("law", "国会成文法"), ("court", "判例"), ("sec", "SEC 规则"), ("fed", "美联储规则"),
          ("finra", "FINRA 规则"), ("fincen", "FinCEN · OFAC"), ("state", "州法")]


def chno():
    """章节 id → 显示的章号，取自 build.py 的目录"""
    import build
    return {f: int(re.search(r"\d+", no)[0]) for f, no, t, p in build.TOC if f.startswith("s") and re.search(r"\d+", no)}

def load():
    rules, seen = [], set()
    for p in sorted((ROOT / "notes").glob("map-*.json")):
        for r in json.loads(p.read_text()):
            if r["id"] not in seen:
                seen.add(r["id"]); rules.append(r)
    return rules

def figure(rules):
    ids = {r["id"] for r in rules}
    ev = [dict(y=y, n=n, t=t, leads=[i for i in leads if i in ids]) for y, n, t, leads in EVENTS]
    data = json.dumps(dict(E=ERAS, V=ev, L=LAYERS, R=rules, C=chno()), ensure_ascii=False)
    return f'''<figure>
  <div class="card">
    <div class="figbar"><div><p class="figtitle">历史时间轴地图：事件与规则</p><p class="figsub">{len(ev)} 个事件、{len(rules)} 条规则。七个时期按规则数量分配宽度，时期内按年份排列，可横向滚动；绿色为 2023–2026 年有变化的规则。点选事件看它引出的规则，点选规则看要求与现状。</p></div></div>
    <div class="hmp lyx-wrap" id="hmp"></div>
    <div class="hmp-d" id="hmp-d" aria-live="polite"></div>
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
body[data-page="h-map"] .wrap{{max-width:min(1280px,94vw)}}
.hmp{{overflow-x:auto}}
.hmp-in{{position:relative;min-width:980px;font-size:11.5px}}
.hmp-era{{display:grid;margin-left:96px}}
.hmp-era div{{border-left:1px solid var(--line);padding:4px 6px 6px;line-height:1.3}}
.hmp-era b{{display:block;font-size:12.5px}}.hmp-era small{{color:var(--faint);font-size:11px}}.hmp-era span{{display:block;color:var(--muted);font-size:11px;margin-top:2px}}
.hmp-row{{display:grid;grid-template-columns:96px 1fr;border-top:1px solid var(--line)}}
.hmp-row>span{{font-size:12px;color:var(--muted);padding:8px 6px 0 0}}
.hmp-row.ev>span{{color:var(--ink);font-weight:600}}
.hmp-tr{{position:relative}}
.hmp-tr i{{position:absolute;top:0;bottom:0;border-left:1px solid var(--line);opacity:.6}}
.hmp-dot{{position:absolute;width:11px;height:11px;margin-left:-5.5px;border-radius:50%;border:2px solid var(--ink);background:var(--card);cursor:pointer;padding:0}}
.hmp-dot.chg{{background:var(--accent);border-color:var(--accent)}}
.hmp-dot.hl{{box-shadow:0 0 0 4px var(--accent-soft);border-color:var(--accent)}}
.hmp-dot.on{{box-shadow:0 0 0 4px var(--ink)}}
.hmp-ev{{position:absolute;font:inherit;font-size:11px;cursor:pointer;border:1px solid var(--ink);background:var(--ink);color:var(--bg);border-radius:6px;padding:2px 6px;white-space:nowrap}}
.hmp-ev.on{{background:var(--accent);border-color:var(--accent);color:#fff}}
.hmp-ax{{display:grid;margin-left:96px;border-top:1px solid var(--line)}}
.hmp-ax div{{position:relative;height:20px;border-left:1px solid var(--line)}}
.hmp-ax em{{position:absolute;top:3px;left:3px;font-style:normal;font-size:11px;color:var(--faint)}}
.hmp-es{{display:block;font-size:11px;color:var(--muted);line-height:1.35;margin-top:2px}}
.hmp-d{{margin-top:12px;background:var(--quote);border-radius:10px;padding:12px 14px;font-size:13.5px;line-height:1.6;min-height:6em}}
.hmp-d b{{font-size:14.5px}}.hmp-d em{{font-style:normal;color:var(--muted);font-size:12.5px;display:block;margin-top:4px}}
.hmp-d ul{{margin:6px 0 0;padding-left:18px}}.hmp-d a{{color:var(--accent);margin-right:12px}}
</style>
<script>
(function(){{
  const D={data},E=D.E,V=D.V,L=D.L,R=D.R,box=document.getElementById('hmp'),det=document.getElementById('hmp-d');

  const ERA=D.E,NE=ERA.length,W=2200;
  const EW=ERA.map(e=>Math.max(1,Math.sqrt(D.R.filter(r=>r.year>=e[0]&&r.year<=e[1]).length))),ES=EW.reduce((a,b)=>a+b,0),EC=EW.map((w,k)=>EW.slice(0,k).reduce((a,b)=>a+b,0)/ES);
  const pos=y=>{{let k=ERA.findIndex(e=>y>=e[0]&&y<=e[1]);if(k<0)k=y<ERA[0][0]?0:NE-1;const e=ERA[k],f=(Math.min(Math.max(y,e[0]),e[1])-e[0]+0.5)/(e[1]-e[0]+1);return EC[k]+f*EW[k]/ES;}};
  const short=n=>{{let s=n.length>16&&n.indexOf('（')>3?n.slice(0,n.indexOf('（')):n;return s.length>18?s.slice(0,17)+'…':s;}};
  function lane(items,cls){{const ends=[];let h='';items.sort((a,b)=>a[0].year-b[0].year).forEach(([r,i])=>{{const t=short(r.name),w=t.length*12.2+16,x=pos(r.year)*W;let k=0;while(ends[k]!==undefined&&x<ends[k]+4)k++;ends[k]=x+w;
      h+='<button type="button" class="'+cls+(r.changed?' chg':'')+'" data-i="'+i+'" style="left:'+x.toFixed(0)+'px;top:'+(6+k*25)+'px" title="'+r.name+'（'+r.year+'）">'+t+'</button>';}});
    return [h,10+ends.length*25];}}
  const eraHead=()=>'<div class="lyx-era" style="width:'+W+'px;grid-template-columns:'+EW.map(w=>w+'fr').join(' ')+'">'+ERA.map(e=>'<div><b>'+e[2]+'</b><small>'+e[0]+'–'+e[1]+'</small></div>').join('')+'</div>';
  const eraGrid=()=>ERA.map((e,k)=>'<i style="left:'+(EC[k]*W)+'px"></i>').join('');
  const lnk=(f,t)=>'<a data-f="'+f+'">'+t+'</a>',lnn=Object.fromEntries(L);
  let h='<div class="lyx-in">'+ERA.map(()=>'').join('')+'<div class="lyx-era" style="width:'+W+'px;grid-template-columns:'+EW.map(w=>w+'fr').join(' ')+'">'+ERA.map(e=>'<div><b>'+e[2]+'</b><small>'+e[0]+'–'+e[1]+'</small><span class="hmp-es">'+e[3]+'</span></div>').join('')+'</div>';
  const ends=[];let evh='';
  V.forEach((v,i)=>{{const t=v.y+' '+v.n,w=t.length*11+18,x=pos(v.y)*W;let k=0;while(ends[k]!==undefined&&x<ends[k]+6)k++;ends[k]=x+w;
    evh+='<button type="button" class="hmp-ev" data-e="'+i+'" style="left:'+x.toFixed(0)+'px;top:'+(6+k*26)+'px">'+t+'</button>';}});
  h+='<div class="lyx-row ev"><span><b>事件</b></span><div class="lyx-tr" style="height:'+(12+ends.length*26)+'px">'+eraGrid()+evh+'</div></div>';
  L.forEach(l=>{{const it=R.map((r,i)=>[r,i]).filter(([r])=>r.layer===l[0]);if(!it.length)return;const [lh,ht]=lane(it,'lyx-c');
    h+='<div class="lyx-row"><span>'+l[1]+'</span><div class="lyx-tr" style="height:'+ht+'px">'+eraGrid()+lh+'</div></div>';}});
  box.innerHTML=h+'</div>';
  const fix=el=>el.querySelectorAll('a[data-f]').forEach(a=>a.setAttribute('href',a.dataset.f+'.'+'html'));
  const dots=[...box.querySelectorAll('.lyx-c')],evs=[...box.querySelectorAll('.hmp-ev')];
  function clear(){{dots.forEach(d=>d.classList.remove('on','hl'));evs.forEach(e=>e.classList.remove('on'));}}
  function showR(i){{clear();const r=R[i];box.querySelector('[data-i="'+i+'"]').classList.add('on');
    det.innerHTML='<b>'+r.name+'</b>（'+r.year+' 年 · '+lnn[r.layer]+'）<br>'+r.req+'<em>现状：'+r.status+'</em>'+(r.g?lnk(r.g,'生成式：第 '+(D.C[r.g]||'')+' 章 →'):'')+(r.d?lnk(r.d,'分解式：阶段 '+(+r.d.slice(1))+' →'):'');fix(det);}}
  function showE(i){{clear();const v=V[i];evs[i].classList.add('on');v.leads.forEach(id=>{{const k=R.findIndex(r=>r.id===id);if(k>=0)box.querySelector('[data-i="'+k+'"]').classList.add('hl');}});
    det.innerHTML='<b>'+v.y+' · '+v.n+'</b><br>'+v.t+(v.leads.length?'<ul>'+v.leads.map(id=>{{const r=R.find(x=>x.id===id);return '<li>'+r.name+'（'+r.year+'）'+(r.g?' '+lnk(r.g,'第 '+(D.C[r.g]||'')+' 章'):'')+'</li>';}}).join('')+'</ul>':'');fix(det);}}
  dots.forEach(d=>d.addEventListener('click',()=>showR(+d.dataset.i)));evs.forEach(e=>e.addEventListener('click',()=>showE(+e.dataset.e)));
  showE(1);
}})();
</script>
'''

if __name__ == "__main__":
    rules = load()
    (ROOT / "figs" / "hmap-history.html").write_text(figure(rules))
    print("历史地图：", len(EVENTS), "个事件，", len(rules), "条规则")
