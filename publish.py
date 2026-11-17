# 用法：python3 publish.py → 重新生成规则地图与全书，复制 site/ 到临时目录并去掉外部字体引用，上传到 VibeClub（内部可见）。
import pathlib, re, shutil, subprocess, tempfile
ROOT = pathlib.Path(__file__).parent
subprocess.run(["python3", "gen_map.py"], cwd=ROOT, check=True)
subprocess.run(["python3", "build.py"], cwd=ROOT, check=True)
tmp = pathlib.Path(tempfile.mkdtemp()) / "site"
shutil.copytree(ROOT / "site", tmp)
for p in tmp.glob("*.html"):
    s = p.read_text()
    s = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", s)
    s = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>\n?', "", s)
    p.write_text(s)
subprocess.run(["vibeclub", "upload", str(tmp), "--slug", "us-finance-law", "--access", "tenant_internal", "--title", "美国金融业法律研究"], check=True)
