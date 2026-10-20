import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ScanFocus } from "../lib/ScanFocus";
import { Strips } from "../lib/Strips";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { ChapterCard, Fade, Ink, Note, Plate, RunningHead } from "../lib/ui";

const S = scene("B3");
const B = beats(S);
const REL = ["六　汉族和少数民族的关系", "七　党和非党的关系", "八　革命和反革命的关系", "九　是非关系"];
const relOf = (i: number) => (i <= 2 ? 0 : i <= 4 ? 1 : i === 5 ? 2 : 3);

/** printed type impression */
export const TypeChar: React.FC<{ ch: string; at: number; size?: number; color?: string }> = ({ ch, at, size = 120, color = C.ink }) => {
  const f = useCurrentFrame();
  const k = ramp(f, at, at + 10);
  return (
    <div
      style={{
        width: size * 1.18,
        height: size * 1.18,
        border: `${Math.max(2, size / 40)}px solid ${color}`,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: F.heavy,
        fontSize: size,
        color,
        lineHeight: 1,
        opacity: k,
        scale: String(1.18 - 0.18 * k),
        filter: "url(#inkEdge)",
      }}
    >
      {ch}
    </div>
  );
};

export const InkEdgeDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="inkEdge">
      <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="9" />
      <feDisplacementMap in="SourceGraphic" scale="2.5" />
    </filter>
  </svg>
);

const Ratio: React.FC = () => {
  const f = useCurrentFrame();
  const W0 = 1300;
  const bar = (y: number, label: string, segs: { v: number; c: string; t: string; hatch?: boolean }[], at: number) => {
    let x = 0;
    return (
      <div style={{ position: "absolute", left: 360, top: y }}>
        <div style={{ position: "absolute", left: -180, top: 30, fontFamily: F.heavy, fontSize: 48, color: C.ink, letterSpacing: 8 }}>{label}</div>
        <div style={{ position: "relative", width: W0, height: 120, border: `2.5px solid ${C.ink}` }}>
          {segs.map((s, i) => {
            const w = s.v * W0 * ramp(f, at + i * 10, at + 40 + i * 10, 0, 1, io);
            const el = (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: x,
                  top: 0,
                  width: w,
                  height: 115,
                  background: s.hatch ? `repeating-linear-gradient(45deg, ${C.red} 0 6px, transparent 6px 14px)` : s.c,
                  display: "flex",
                  alignItems: "center",
                  paddingLeft: 22,
                  overflow: "hidden",
                }}
              >
                <span style={{ fontFamily: F.heavy, fontSize: 36, color: s.hatch ? C.red : s.c === C.ink || s.c === C.red ? C.paperHi : C.ink, whiteSpace: "nowrap", background: s.hatch ? C.paper : "none", padding: s.hatch ? "0 8px" : 0 }}>{s.t}</span>
              </div>
            );
            x += s.v * W0;
            return el;
          })}
        </div>
      </div>
    );
  };
  return (
    <AbsoluteFill>
      {bar(280, "人口", [
        { v: 0.94, c: C.ink, t: "汉族 94%" },
        { v: 0.06, c: C.red, t: "" },
      ], 4)}
      <Ink at={40} style={{ position: "absolute", left: 1680, top: 300 }}>
        <div style={{ fontFamily: F.song, fontSize: 32, color: C.red, whiteSpace: "nowrap" }}>少数民族</div>
      </Ink>
      {bar(560, "土地", [
        { v: 0.5, c: C.red, t: "少数民族地区 50%" },
        { v: 0.1, c: C.red, t: "～60%", hatch: true },
        { v: 0.4, c: C.paper2, t: "" },
      ], 60)}
      <Ink at={110}>
        <div style={{ position: "absolute", top: 780, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.gray, letterSpacing: 8 }}>“人口众多” · “地大物博”</div>
      </Ink>
    </AbsoluteFill>
  );
};

const Sixteen: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const eight = "长期共存互相监督";
  const more = "肝胆相照荣辱与共";
  const t2 = Math.min(len * 0.45, 120);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <Ink at={0}>
        <div style={{ fontFamily: F.song, fontSize: 34, color: C.gray, letterSpacing: 8, marginBottom: 40, textAlign: "center" }}>一九五六 · 八字方针</div>
      </Ink>
      <div style={{ display: "flex", gap: 22 }}>
        {[...eight].map((c, i) => (
          <React.Fragment key={i}>
            <TypeChar ch={c} at={10 + i * 6} size={96} />
            {i === 3 && <div style={{ width: 30 }} />}
          </React.Fragment>
        ))}
      </div>
      <div style={{ display: "flex", gap: 22, marginTop: 34 }}>
        {[...more].map((c, i) => (
          <React.Fragment key={i}>
            <TypeChar ch={c} at={t2 + i * 6} size={96} color={C.red} />
            {i === 3 && <div style={{ width: 30 }} />}
          </React.Fragment>
        ))}
      </div>
      <Ink at={t2 + 50}>
        <div style={{ fontFamily: F.song, fontSize: 34, color: C.red, letterSpacing: 8, marginTop: 40, textAlign: "center" }}>后来 · 十六字方针</div>
      </Ink>
      <span style={{ display: "none" }}>{f}</span>
    </AbsoluteFill>
  );
};

/** negative factors turned into positive ones */
const Convert: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const N = 60;
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", top: 180, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 56, color: C.ink, letterSpacing: 10 }}>一定要分清敌我</div>
      </Ink>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: N }, (_, i) => {
          const c = i % 15;
          const r = Math.floor(i / 15);
          const x = 510 + c * 64;
          const y = 380 + r * 64;
          const conv = i % 11 === 0 ? 0 : ramp(f, 60 + ((i * 37) % N) * ((len - 140) / N), 80 + ((i * 37) % N) * ((len - 140) / N));
          return (
            <g key={i}>
              <circle cx={x} cy={y} r={15} fill={C.ink} opacity={1 - conv} />
              <circle cx={x} cy={y} r={15 * (0.4 + 0.6 * conv)} fill={C.red} opacity={conv} />
            </g>
          );
        })}
      </svg>
      <div style={{ position: "absolute", top: 680, width: "100%", display: "flex", justifyContent: "center", gap: 60, fontFamily: F.song, fontSize: 36, letterSpacing: 6 }}>
        <span style={{ color: C.ink }}>● 消极因素</span>
        <span style={{ color: C.gray }}>→</span>
        <span style={{ color: C.red }}>● 积极因素</span>
      </div>
      <Ink at={len - 120}>
        <div style={{ position: "absolute", top: 780, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 6 }}>给以生活出路，使他们有自新的机会</div>
      </Ink>
    </AbsoluteFill>
  );
};

const Couplet: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "row", gap: 160 }}>
    {["惩前毖后", "治病救人"].map((w, j) => (
      <div key={j} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {[...w].map((c, i) => (
          <TypeChar key={i} ch={c} at={6 + j * 26 + i * 6} size={110} color={j ? C.red : C.ink} />
        ))}
      </div>
    ))}
  </AbsoluteFill>
);

const LookHelp: React.FC = () => {
  const f = useCurrentFrame();
  const k = ramp(f, 30, 70, 0, 1, io);
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", top: 230, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 66, color: C.ink, letterSpacing: 18 }}>一要看 · 二要帮</div>
      </Ink>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={560} y1={520} x2={560 + 800 * k} y2={520} stroke={C.ink} strokeWidth={3} />
        <circle cx={560} cy={520} r={22} fill={C.ink} />
        <circle cx={1360} cy={520} r={22} fill={C.red} opacity={k > 0.98 ? 1 : 0} />
        <path d="M948,546 L960,526 L972,546 Z" fill={C.red} opacity={k > 0.98 ? 1 : 0} />
      </svg>
      <Ink at={20} style={{ position: "absolute", left: 560, top: 580, translate: "-50% 0" }}>
        <div style={{ fontFamily: F.heavy, fontSize: 48, color: C.ink, letterSpacing: 6, whiteSpace: "nowrap" }}>分清是非</div>
      </Ink>
      <Ink at={70} style={{ position: "absolute", left: 1360, top: 580, translate: "-50% 0" }}>
        <div style={{ fontFamily: F.heavy, fontSize: 48, color: C.red, letterSpacing: 6, whiteSpace: "nowrap" }}>治病救人</div>
      </Ink>
      <Ink at={90}>
        <div style={{ position: "absolute", top: 700, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.gray, letterSpacing: 8 }}>出发点和归宿都是团结</div>
      </Ink>
    </AbsoluteFill>
  );
};

const Extremes: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 150, top: 260, width: 820 }}>
        {[
          ["只讲斗争", "残酷斗争、无情打击"],
          ["只讲团结", "和稀泥"],
        ].map(([a, b], i) => (
          <Ink key={i} at={10 + i * 50} style={{ marginBottom: 70 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
              <span style={{ fontFamily: F.heavy, fontSize: 52, color: C.ink, letterSpacing: 6 }}>{a}</span>
              <span style={{ fontFamily: F.song, fontSize: 40, color: C.gray }}>→</span>
              <span style={{ fontFamily: F.song, fontSize: 44, color: C.gray, textDecoration: `line-through ${C.red} 3px`, letterSpacing: 4 }}>{b}</span>
            </div>
          </Ink>
        ))}
        <Ink at={110}>
          <div style={{ fontFamily: F.heavy, fontSize: 58, color: C.red, letterSpacing: 10, marginTop: 20 }}>分寸</div>
        </Ink>
      </div>
      <Note at={150} label="研读体会" lines={["面对网络上", "“一棍子打死”的舆论，", "这份分寸更显珍贵。"]} x={1180} y={300} w={640} size={46} perLine={36} />
      <span style={{ display: "none" }}>{f}</span>
    </AbsoluteFill>
  );
};

export const B3: React.FC = () => {
  const L = S.lines.map((_, i) => B(i));
  const c0 = L[0].a;
  const f = useCurrentFrame();
  const end = (i: number) => (L[i + 1]?.a ?? S.dur) + 6;
  const len = (a: number, b: number) => end(b) - L[a].a + 6;
  const cur = Math.max(0, L.findIndex((l, i) => f >= l.a - 6 && f < end(i) - 6));
  return (
    <AbsoluteFill>
      <InkEdgeDefs />
      <Fade a={0} b={c0 + 4} fi={10} fo={10}>
        <ChapterCard {...S.card!} len={c0 + 4} />
      </Fade>
      <Fade a={L[0].a - 6} b={end(0)}>
        <Ratio />
      </Fade>
      <Fade a={L[1].a - 6} b={end(1)}>
        <Strips items={[{ page: "p20", find: "实际上是汉族“人口众多”，少" }, { page: "p21", find: "数民族“地大物博”" }]} at={14} per={Math.round((L[1].d - 20) / 2)} seed={81} />
      </Fade>
      <Fade a={L[2].a - 6} b={end(2)}>
        <Plate name="kongqi_senlin_baozang" len={len(2, 2)} oy={[30, -30]} />
        <Ink at={20} style={{ position: "absolute", left: 120, top: 120 }}>
          <div style={{ fontFamily: F.song, fontSize: 30, color: C.ink, letterSpacing: 4, background: "rgba(237,229,212,0.9)", padding: "8px 18px", lineHeight: 1.6 }}>
            “天上的空气，地上的森林，地下的宝藏，
            <br />
            都是建设社会主义所需要的重要因素”
          </div>
        </Ink>
      </Fade>
      <Fade a={L[3].a - 6} b={end(3)}>
        <ScanFocus marks={[{ page: "p22", find: "究竟是一个党好，还是几个党好？现在看来，恐怕是几个党好" }]} at={14} dur={L[3].d - 30} len={len(3, 3)} seed={83} />
      </Fade>
      <Fade a={L[4].a - 6} b={end(4)}>
        <Sixteen len={len(4, 4)} />
      </Fade>
      <Fade a={L[5].a - 6} b={end(5)}>
        <Convert len={len(5, 5)} />
      </Fade>
      <Fade a={L[6].a - 6} b={end(6)}>
        <Couplet />
      </Fade>
      <Fade a={L[7].a - 6} b={end(7)}>
        <Plate name="aq" len={len(7, 7)} />
      </Fade>
      <Fade a={L[8].a - 6} b={end(8)}>
        <LookHelp />
      </Fade>
      <Fade a={L[9].a - 6} b={S.dur}>
        <Extremes />
      </Fade>
      {f > c0 - 10 && <RunningHead block="叁 · 社会生态与政治关系" rel={REL[relOf(cur)]} at={c0 - 10} />}
    </AbsoluteFill>
  );
};
