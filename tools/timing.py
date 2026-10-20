"""script.json -> video/src/data/timeline.json + docs/字幕.srt + docs/配音稿.md"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "docs/script.json").read_text(encoding="utf8"))
M = S["meta"]
FPS = M["fps"]
MAXC = 20

SOFT = "，、；：,"
HARD = "。？！?!…"


def spoken_len(t):
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t))


def line_secs(line):
    t = line["t"]
    cps = M["cpsQuote"] if line.get("q") else M["cps"]
    s = spoken_len(t) / cps
    s += 0.13 * sum(t.count(c) for c in SOFT) + 0.28 * sum(t.count(c) for c in HARD)
    return s


def chunks(t):
    parts = re.findall(r"[^，、；：。？！]+[，、；：。？！]?[”’」]*", t)
    out, cur = [], ""
    for p in parts:
        if cur and spoken_len(cur + p) > MAXC:
            out.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        out.append(cur)
    return [re.sub(r"[，、；：。]+(?=[”’」]*$)", "", c) for c in out]


def fmt(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


t = 0.0
timeline = {"fps": FPS, "scenes": []}
srt = []
doc = ["# 配音稿（带时间码）", "",
       f"语速基准：叙述约 {M['cps']} 字/秒，原文引用约 {M['cpsQuote']} 字/秒；每句之间留约 {M['gap']} 秒气口。",
       "【原文】为《论十大关系》原句，请放慢、读得沉稳；【研读】是我们小组的追问与体会，语气转为思考、提问。",
       "每句录成一条音频，按句首编号命名（如 `B1_07.wav`）放进 `assets/vo/`，再运行 `python tools/fit_voice.py`，整片会按真实配音时长自动重排。", ""]
n = 1
for sc in S["scenes"]:
    start = t
    t += sc.get("pre", 0)
    lines = []
    for li, ln in enumerate(sc["lines"]):
        ln = {**ln, "id": f"{sc['id']}_{li + 1:02d}"}
        d = ln.get("sec") or line_secs(ln)
        cs = chunks(ln["t"])
        weights = [max(spoken_len(c), 1) for c in cs]
        tot = sum(weights)
        cur = t
        subs = []
        for c, w in zip(cs, weights):
            dd = d * w / tot
            subs.append({"text": c, "from": round(cur * FPS), "to": round((cur + dd) * FPS)})
            srt.append(f"{n}\n{fmt(cur)} --> {fmt(cur + dd)}\n{c}\n")
            n += 1
            cur += dd
        lines.append({**ln, "from": round(t * FPS), "to": round((t + d) * FPS), "subs": subs})
        t += d + M["gap"]
    if sc["lines"]:
        t -= M["gap"]
    t += sc.get("post", 0)
    if "fixed" in sc:
        t = max(t, start + sc["fixed"])
    dur = round(t * FPS) - round(start * FPS)
    timeline["scenes"].append({"id": sc["id"], "name": sc["name"], "from": round(start * FPS), "dur": dur,
                               "card": sc.get("card"), "lines": [{**l, "from": l["from"] - round(start * FPS), "to": l["to"] - round(start * FPS),
                                                                   "subs": [{**s, "from": s["from"] - round(start * FPS), "to": s["to"] - round(start * FPS)} for s in l["subs"]]} for l in lines]})
    doc.append(f"## {sc['id']}　{sc['name']}　〔{fmt(start)[:-4]} – {fmt(t)[:-4]}，{t - start:.1f} 秒〕")
    doc.append("")
    for l in lines:
        tag = "【原文】" if l.get("q") else ("【研读】" if l.get("ask") else "")
        doc.append(f"- `{l['id']}` `{fmt(l['from'] / FPS)[3:-4]}` {tag}{l['t']}")
        doc.append(f"  - 画面：{l.get('v', '')}")
    doc.append("")

timeline["total"] = round(t * FPS)
timeline["meta"] = M
doc.insert(4, f"全片时长：约 {int(t // 60)} 分 {t % 60:.0f} 秒（{timeline['total']} 帧 @ {FPS}fps）")
doc.insert(5, "")
(ROOT / "video/src/data").mkdir(parents=True, exist_ok=True)
(ROOT / "video/src/data/timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf8")
(ROOT / "docs/字幕.srt").write_text("\n".join(srt), encoding="utf8")
(ROOT / "docs/配音稿.md").write_text("\n".join(doc), encoding="utf8")
for s in timeline["scenes"]:
    print(f"{s['id']:4s} {s['from'] / FPS:7.1f}s  +{s['dur'] / FPS:6.1f}s  {s['name']}")
print("TOTAL", f"{t:.1f}s")
