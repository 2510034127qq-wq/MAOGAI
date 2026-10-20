import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { Factory, Gear } from "../lib/glyphs";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { ChapterCard, Fade, hasAsset, Ink, Note, Plate, RunningHead } from "../lib/ui";

const S = scene("B1");
const B = beats(S);
const REL = ["一　重工业和轻工业、农业的关系", "二　沿海工业和内地工业的关系", "三　经济建设和国防建设的关系"];
const relOf = (i: number) => (i <= 4 ? 0 : i <= 7 ? 1 : 2);

const Lbl: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ position: "absolute", fontFamily: F.song, fontSize: 34, color: C.ink, letterSpacing: 4, whiteSpace: "nowrap", ...style }}>{children}</div>
);

/** Soviet one-sidedness: one tall bar, two stunted ones */
const OneSided: React.FC = () => {
  const f = useCurrentFrame();
  const g = ramp(f, 10, 60, 0, 1, io);
  const tilt = ramp(f, 70, 110, 0, 1, io);
  const bars = [
    { n: "重工业", h: 480 * g, c: C.ink },
    { n: "轻工业", h: 46 * g, c: C.gray },
    { n: "农业", h: 40 * g, c: C.gray },
  ];
  return (
    <AbsoluteFill>
      <Ink at={2}>
        <div style={{ position: "absolute", top: 150, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 8 }}>苏联和一些东欧国家：片面地注重重工业</div>
      </Ink>
      <div style={{ position: "absolute", left: 600, top: 300, width: 520, height: 500, rotate: `${tilt * 4}deg`, transformOrigin: "50% 100%" }}>
        {bars.map((b, i) => (
          <div key={i} style={{ position: "absolute", bottom: 0, left: i * 180, width: 120, height: b.h, background: b.c }} />
        ))}
      </div>
      <div style={{ position: "absolute", left: 560, top: 800, width: 620, height: 3, background: C.ink }} />
      {bars.map((b, i) => (
        <Lbl key={i} style={{ left: 600 + i * 180, top: 820, width: 120, textAlign: "center", fontSize: 32 }}>
          {b.n}
        </Lbl>
      ))}
      {["市场上的货物不够", "货币不稳定"].map((t, i) => (
        <Ink key={i} at={80 + i * 14} style={{ position: "absolute", left: 1260, top: 470 + i * 80 }}>
          <div style={{ fontFamily: F.song, fontSize: 44, color: C.gray, letterSpacing: 6 }}>— {t}</div>
        </Ink>
      ))}
    </AbsoluteFill>
  );
};

/** investment shares (schematic): heavy still largest, agriculture & light weighted up */
const Shares: React.FC = () => {
  const f = useCurrentFrame();
  const k = ramp(f, 40, 90, 0, 1, io);
  const seg = [
    { n: "重工业", v: 0.64 - 0.08 * k, c: C.ink, t: C.paper },
    { n: "轻工业", v: 0.17 + 0.04 * k, c: C.red, t: C.paperHi },
    { n: "农业", v: 0.19 + 0.04 * k, c: "#C9675F", t: C.paperHi },
  ];
  let x = 0;
  const W0 = 1400;
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", top: 230, left: 260, fontFamily: F.song, fontSize: 36, color: C.gray, letterSpacing: 6 }}>
          投资比例 <span style={{ fontSize: 26 }}>（示意）</span>
        </div>
      </Ink>
      <div style={{ position: "absolute", left: 260, top: 300, width: W0, height: 150, opacity: ramp(f, 0, 16) }}>
        {seg.map((s, i) => {
          const w = s.v * W0;
          const el = (
            <div key={i} style={{ position: "absolute", left: x, top: 0, width: w - 4, height: 150, background: s.c, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontFamily: F.heavy, fontSize: 44, color: s.t, letterSpacing: 6 }}>{s.n}</span>
            </div>
          );
          x += w;
          return el;
        })}
      </div>
      <Ink at={20} style={{ position: "absolute", left: 260, top: 490 }}>
        <div style={{ fontFamily: F.song, fontSize: 40, color: C.ink, letterSpacing: 6 }}>还是为主，还是投资的重点</div>
      </Ink>
      <Ink at={70} style={{ position: "absolute", right: 260, top: 490, textAlign: "right" }}>
        <div style={{ fontFamily: F.kai, fontSize: 48, color: C.red, letterSpacing: 6 }}>比例要加重一点 ↑</div>
      </Ink>
    </AbsoluteFill>
  );
};

/** accumulation loop */
const Flow: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const nodes = [
    { id: "nong", x: 420, y: 360, t: "农业", r: 82 },
    { id: "qing", x: 420, y: 640, t: "轻工业", r: 82 },
    { id: "life", x: 960, y: 330, t: "人民生活的需要", r: 0 },
    { id: "acc", x: 960, y: 670, t: "资金的积累", r: 0 },
    { id: "zhong", x: 1500, y: 500, t: "重工业", r: 96 },
  ];
  const N = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const edges: [string, string, number][] = [
    ["nong", "life", 10],
    ["qing", "life", 16],
    ["nong", "acc", 22],
    ["qing", "acc", 28],
    ["acc", "zhong", 46],
    ["life", "zhong", 52],
  ];
  const grow = ramp(f, 60, len - 20, 1, 1.28, io);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {edges.map(([a, b, at], i) => {
          const A = N[a];
          const Bn = N[b];
          const x0 = A.x + (A.r || 150);
          const x1 = Bn.x - (Bn.r ? Bn.r * (b === "zhong" ? grow : 1) : 150);
          const d = `M${x0},${A.y} C${(x0 + x1) / 2},${A.y} ${(x0 + x1) / 2},${Bn.y} ${x1},${Bn.y}`;
          const k = ramp(f, at, at + 26, 0, 1, io);
          return (
            <g key={i}>
              <path d={d} stroke={C.ink} strokeWidth={2} fill="none" strokeDasharray={900} strokeDashoffset={900 * (1 - k)} opacity={0.75} />
              {k >= 1 &&
                [0, 1, 2].map((j) => {
                  const p = ((f - at - 26) / 70 + j / 3) % 1;
                  const t = p;
                  const mx = (x0 + x1) / 2;
                  const bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * mx + 3 * (1 - t) * t * t * mx + t ** 3 * x1;
                  const by = (1 - t) ** 3 * A.y + 3 * (1 - t) ** 2 * t * A.y + 3 * (1 - t) * t * t * Bn.y + t ** 3 * Bn.y;
                  return <circle key={j} cx={bx} cy={by} r={5} fill={C.red} />;
                })}
            </g>
          );
        })}
        {nodes
          .filter((n) => n.r)
          .map((n) => (
            <circle key={n.id} cx={n.x} cy={n.y} r={n.r * (n.id === "zhong" ? grow : 1)} fill={n.id === "zhong" ? C.ink : C.paperHi} stroke={C.ink} strokeWidth={2.5} opacity={ramp(f, 0, 14)} />
          ))}
      </svg>
      {nodes.map((n) => (
        <div
          key={n.id}
          style={{
            position: "absolute",
            left: n.x,
            top: n.y,
            translate: "-50% -50%",
            fontFamily: n.r ? F.heavy : F.song,
            fontSize: n.r ? (n.id === "zhong" ? 46 : 38) : 38,
            color: n.id === "zhong" ? C.paper : C.ink,
            letterSpacing: 4,
            whiteSpace: "nowrap",
            opacity: n.r ? ramp(f, 0, 14) : ramp(f, 20, 40),
            borderBottom: n.r ? "none" : `2px solid ${C.red}`,
            paddingBottom: n.r ? 0 : 6,
          }}
        >
          {n.t}
        </div>
      ))}
      <Ink at={4}>
        <div style={{ position: "absolute", top: 150, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 40, color: C.red, letterSpacing: 8 }}>加重的结果</div>
      </Ink>
      <Ink at={len - 70}>
        <div style={{ position: "absolute", top: 820, width: "100%", textAlign: "center", fontFamily: F.song, fontSize: 36, color: C.gray, letterSpacing: 6 }}>“几十年后算总账”</div>
      </Ink>
    </AbsoluteFill>
  );
};

const COAST = ["辽宁", "河北", "北京", "天津", "河南东部", "山东", "安徽", "江苏", "上海", "浙江", "福建", "广东", "广西"];

const Dots: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", left: 230, top: 210, fontFamily: F.song, fontSize: 30, color: C.gray, letterSpacing: 6 }}>原文所谓“沿海”</div>
      </Ink>
      <div style={{ position: "absolute", left: 230, top: 270, display: "grid", gridTemplateColumns: "repeat(2, 200px)", rowGap: 16 }}>
        {COAST.map((p, i) => (
          <Ink key={p} at={6 + i * 3} d={14}>
            <div style={{ fontFamily: F.song, fontSize: 38, color: C.ink, letterSpacing: 4 }}>{p}</div>
          </Ink>
        ))}
      </div>
      <svg width={620} height={620} style={{ position: "absolute", left: 900, top: 230 }}>
        {Array.from({ length: 100 }, (_, i) => {
          const r = Math.floor(i / 10);
          const c = i % 10;
          const k = ramp(f, 20 + i * 0.9, 30 + i * 0.9);
          return <circle key={i} cx={31 + c * 62} cy={31 + r * 62} r={22 * k} fill={i < 70 ? C.red : C.ink} />;
        })}
      </svg>
      <Ink at={70} style={{ position: "absolute", left: 1560, top: 300 }}>
        <div style={{ fontFamily: F.heavy, fontSize: 96, color: C.red, lineHeight: 1 }}>70%</div>
        <div style={{ fontFamily: F.song, fontSize: 36, color: C.ink, letterSpacing: 6, marginTop: 10 }}>在沿海</div>
      </Ink>
      <Ink at={96} style={{ position: "absolute", left: 1560, top: 600 }}>
        <div style={{ fontFamily: F.heavy, fontSize: 96, color: C.ink, lineHeight: 1 }}>30%</div>
        <div style={{ fontFamily: F.song, fontSize: 36, color: C.ink, letterSpacing: 6, marginTop: 10 }}>在内地</div>
      </Ink>
    </AbsoluteFill>
  );
};

const Diptych: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const t = ramp(f, 0, len, 0, 1, (x) => x);
  const arrow = ramp(f, 40, 80, 0, 1, io);
  const half = (name: string, x: number) => (
    <div style={{ position: "absolute", left: x, top: 0, width: 960, height: 1080, overflow: "hidden" }}>
      {hasAsset(`img:${name}`) ? (
        <Img src={staticFile(`img/${name}_paper.png`)} style={{ width: 1920, height: 1080, objectFit: "cover", translate: `-480px 0`, scale: String(1.02 + 0.05 * t) }} />
      ) : (
        <div style={{ margin: 300, fontFamily: F.serif, fontSize: 36, color: C.gray }}>木刻待生成：{name}</div>
      )}
    </div>
  );
  return (
    <AbsoluteFill>
      {half("yanhai", 0)}
      {half("neidi", 960)}
      <div style={{ position: "absolute", left: 958, top: 0, width: 4, height: 1080, background: C.paper }} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <path d={`M760,180 Q960,110 ${760 + 400 * arrow},180`} stroke={C.red} strokeWidth={6} fill="none" />
        {arrow > 0.98 && <path d="M1160,180 l-30,-22 l4,30 Z" fill={C.red} />}
      </svg>
      <Ink at={70} style={{ position: "absolute", left: 0, width: 1920, top: 70, textAlign: "center" }}>
        <span style={{ fontFamily: F.kai, fontSize: 44, color: C.red, background: "rgba(237,229,212,0.85)", padding: "4px 18px", letterSpacing: 8 }}>支持</span>
      </Ink>
      {[
        ["沿海 · 工业老底子", 80],
        ["内地 · 新的工业大部分摆在这里", 1040],
      ].map(([t2, x], i) => (
        <Ink key={i} at={10 + i * 12} style={{ position: "absolute", left: x as number, top: 820 }}>
          <span style={{ fontFamily: F.song, fontSize: 36, color: C.ink, background: "rgba(237,229,212,0.88)", padding: "6px 18px", letterSpacing: 4 }}>{t2}</span>
        </Ink>
      ))}
    </AbsoluteFill>
  );
};

const Factories: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const groups = [
    { n: 3, t: "三个厂", clip: 1 },
    { n: 2, t: "两个厂", clip: 1 },
    { n: 1, t: "一个厂", clip: 1 },
    { n: 1, t: "至少半个厂", clip: 0.5 },
  ];
  const step = (len - 50) / 4;
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", top: 210, width: "100%", textAlign: "center", fontFamily: F.song, fontSize: 38, color: C.gray, letterSpacing: 6 }}>轻工业工厂 · 四年之内 · 除了收回本厂的投资以外</div>
      </Ink>
      <div style={{ position: "absolute", top: 400, left: 0, width: 1920, display: "flex", justifyContent: "center", gap: 90 }}>
        {groups.map((g, gi) => {
          const at = 30 + gi * step;
          return (
            <div key={gi} style={{ textAlign: "center", opacity: ramp(f, at, at + 14) }}>
              <div style={{ display: "flex", gap: 8, justifyContent: "center", height: 110, alignItems: "flex-end" }}>
                {Array.from({ length: g.n }, (_, j) => (
                  <div key={j} style={{ translate: `0 ${(1 - ramp(f, at + j * 5, at + j * 5 + 16)) * 20}px` }}>
                    <Factory w={120} clip={g.clip} color={gi === 0 ? C.ink : C.ink} />
                  </div>
                ))}
              </div>
              <div style={{ fontFamily: F.heavy, fontSize: 44, color: gi === 3 ? C.red : C.ink, letterSpacing: 4, marginTop: 30 }}>{g.t}</div>
            </div>
          );
        })}
      </div>
      <Ink at={len - 40}>
        <div style={{ position: "absolute", top: 740, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 6 }}>“这样好的事情为什么不做？”</div>
      </Ink>
    </AbsoluteFill>
  );
};

/** budget bar 30% → 20%, freed share turns into factories & machines */
const Budget: React.FC<{ t9: number; len: number }> = ({ t9, len }) => {
  const f = useCurrentFrame();
  const W0 = 1400;
  const shrink = ramp(f, t9 + 20, t9 + 60, 0, 1, io);
  const lift = ramp(f, t9 + 50, t9 + 100, 0, 1, io);
  const mil = 0.3 - 0.1 * shrink;
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", left: 260, top: 210, fontFamily: F.song, fontSize: 36, color: C.gray, letterSpacing: 6 }}>国家预算全部支出</div>
      </Ink>
      <div style={{ position: "absolute", left: 260, top: 280, width: W0, height: 140, border: `2.5px solid ${C.ink}`, opacity: ramp(f, 0, 14) }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: W0 * mil * ramp(f, 10, 40, 0, 1, io), background: C.red, display: "flex", alignItems: "center", paddingLeft: 26 }}>
          <span style={{ fontFamily: F.heavy, fontSize: 40, color: C.paperHi, letterSpacing: 4, whiteSpace: "nowrap", opacity: ramp(f, 30, 44) }}>军政费用 {Math.round(mil * 100)}%</span>
        </div>
        {shrink > 0 && (
          <div
            style={{
              position: "absolute",
              left: W0 * 0.2,
              top: 0,
              width: W0 * 0.1,
              height: 136,
              border: `3px dashed ${C.red}`,
              translate: `${lift * 420}px ${lift * 330}px`,
              opacity: 1 - ramp(f, t9 + 80, t9 + 100),
            }}
          />
        )}
      </div>
      <Ink at={t9 + 10} style={{ position: "absolute", left: 260, top: 450 }}>
        <div style={{ fontFamily: F.song, fontSize: 34, color: C.gray, letterSpacing: 6 }}>
          第一个五年计划期间 <span style={{ color: C.red }}>30%</span>　→　第二个五年计划 <span style={{ color: C.red }}>20% 左右</span>
        </div>
      </Ink>
      <div style={{ position: "absolute", left: 640, top: 600, display: "flex", gap: 40, alignItems: "flex-end", opacity: ramp(f, t9 + 90, t9 + 110) }}>
        <Factory w={130} />
        <Factory w={130} />
        <Gear w={110} rot={f * 0.6} />
        <Gear w={80} rot={-f * 0.8} />
      </div>
      <Ink at={t9 + 100} style={{ position: "absolute", left: 1310, top: 600 }}>
        <div style={{ fontFamily: F.kai, fontSize: 46, color: C.red, letterSpacing: 6, lineHeight: 1.5 }}>
          多开些工厂
          <br />
          多造些机器
        </div>
      </Ink>
      <span style={{ display: "none" }}>{len}</span>
    </AbsoluteFill>
  );
};

const Date1964: React.FC = () => {
  const f = useCurrentFrame();
  const k = ramp(f, 40, 52);
  const line = ramp(f, 4, 40, 0, 1, io);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <svg width={1200} height={120}>
        <line x1={100} y1={60} x2={100 + 1000 * line} y2={60} stroke={C.ink} strokeWidth={2} />
        {Array.from({ length: 9 }, (_, i) => (
          <line key={i} x1={100 + i * 125} x2={100 + i * 125} y1={50} y2={70} stroke={C.ink} strokeWidth={2} opacity={line * 9 > i ? 1 : 0} />
        ))}
        <circle cx={100} cy={60} r={10} fill={C.ink} />
        <circle cx={1100} cy={60} r={10} fill={C.red} opacity={line > 0.98 ? 1 : 0} />
        <text x={100} y={112} textAnchor="middle" fontFamily="STSong" fontSize={30} fill={C.gray}>
          1956
        </text>
        <text x={1100} y={112} textAnchor="middle" fontFamily="STSong" fontSize={30} fill={C.red}>
          1964
        </text>
        <text x={600} y={34} textAnchor="middle" fontFamily="STKai" fontSize={32} fill={C.gray}>
          八年
        </text>
      </svg>
      <div style={{ fontFamily: F.heavy, fontSize: 190, color: C.ink, letterSpacing: 10, marginTop: 50, opacity: k, scale: String(1.08 - 0.08 * k), filter: `blur(${(1 - k) * 4}px)` }}>1964 · 10 · 16</div>
      <Ink at={60}>
        <div style={{ fontFamily: F.song, fontSize: 48, color: C.gray, letterSpacing: 12, marginTop: 30 }}>中国第一颗原子弹爆炸成功</div>
      </Ink>
      <AbsoluteFill style={{ backgroundColor: "#FBF8F1", opacity: Math.max(0, ramp(f, 44, 48) - ramp(f, 48, 80)) * 0.8, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};

export const B1: React.FC = () => {
  const L = S.lines.map((_, i) => B(i));
  const c0 = L[0].a;
  const f = useCurrentFrame();
  const rel = REL[relOf(L.findIndex((l, i) => f >= l.a - 6 && f < (L[i + 1]?.a ?? S.dur) - 6))] ?? REL[0];
  const end = (i: number) => (L[i + 1]?.a ?? S.dur) + 6;
  return (
    <AbsoluteFill>
      <Fade a={0} b={c0 + 4} fi={10} fo={10}>
        <ChapterCard {...S.card!} len={c0 + 4} />
      </Fade>
      <Fade a={L[0].a - 6} b={end(0)}>
        <Plate name="nongqingzhong" len={end(0) - L[0].a + 6} />
      </Fade>
      <Fade a={L[1].a - 6} b={end(1)}>
        <ScanFocus marks={[{ page: "p08", find: "如果没有足够的粮食和其他生活必需品，首先就不能养活工人，还谈什么发展重工业" }]} at={14} dur={L[1].d - 40} len={end(1) - L[1].a + 6} seed={61} />
      </Fade>
      <Fade a={L[2].a - 6} b={end(2)}>
        <OneSided />
      </Fade>
      <Fade a={L[3].a - 6} b={end(3)}>
        <Shares />
      </Fade>
      <Fade a={L[4].a - 6} b={end(4)}>
        <Flow len={end(4) - L[4].a + 6} />
      </Fade>
      <Fade a={L[5].a - 6} b={end(5)}>
        <Dots />
      </Fade>
      <Fade a={L[6].a - 6} b={end(6)}>
        <Diptych len={end(6) - L[6].a + 6} />
      </Fade>
      <Fade a={L[7].a - 6} b={end(7)}>
        <Factories len={end(7) - L[7].a + 6} />
      </Fade>
      <Fade a={L[8].a - 6} b={end(9)}>
        <Budget t9={L[9].a - L[8].a + 6} len={end(9) - L[8].a + 6} />
      </Fade>
      <Fade a={L[10].a - 6} b={end(10)}>
        <ScanFocus marks={[{ page: "p12", find: "只有经济建设发展得更快了，国防建设才能够有更大的进步" }]} at={14} dur={L[10].d - 36} len={end(10) - L[10].a + 6} seed={63} />
      </Fade>
      <Fade a={L[11].a - 6} b={end(11)}>
        <Date1964 />
      </Fade>
      <Fade a={L[12].a - 6} b={S.dur}>
        <div style={{ position: "absolute", left: 60, top: 140, width: 980, height: 700, overflow: "hidden" }}>
          <ScanFocus marks={[{ page: "p11", find: "新的侵华战争和新的世界大战，估计短时期内打不起来" }]} w={980} h={700} cy={330} at={10} dur={60} len={S.dur - L[12].a} fitW={940} fitH={300} maxScale={1.0} seed={65} />
        </div>
        <Note at={50} label="研读追问" lines={["前提：“短时期内打不起来”。", "技术迭代极快的今天，", "发展与安全的时间窗口，", "还像当年那样充裕吗？"]} x={1120} y={240} perLine={40} />
      </Fade>
      {f > c0 - 10 && <RunningHead block="壹 · 经济结构与空间布局" rel={rel} at={c0 - 10} />}
    </AbsoluteFill>
  );
};
