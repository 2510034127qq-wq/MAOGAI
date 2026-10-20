import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { PAIRS, PairRow } from "../lib/pairs";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { Fade, FrameSeq, Ink, Write } from "../lib/ui";

const S = scene("S7");
const B = beats(S);

const Level: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      {PAIRS.map((_, i) => {
        const t0 = ((i * 7) % 5) * 3;
        const tilt = (i % 2 ? 1 : -1) * (6 + ((i * 13) % 6)) * (1 - ramp(f, 14 + t0, 50 + t0, 0, 1, io));
        return (
          <div key={i} style={{ position: "absolute", left: 960, top: 140 + i * 68, translate: "-50% -50%", opacity: ramp(f, i, i + 10) }}>
            <PairRow i={i} size={38} lineW={220} tilt={tilt} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const PoLi: React.FC = () => (
  <AbsoluteFill>
    <FrameSeq shot="leadtype_poli" />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 150, display: "flex", justifyContent: "center", gap: 120 }}>
      {[
        ["破", "对苏联模式的迷信 · 只顾一头的片面", C.ink],
        ["立", "从中国实际出发 · 统筹兼顾的建设思路", C.red],
      ].map(([a, b, c], i) => (
        <Ink key={i} at={30 + i * 60}>
          <div style={{ display: "flex", alignItems: "center", gap: 20, background: "rgba(237,229,212,0.9)", padding: "14px 30px" }}>
            <span style={{ fontFamily: F.heavy, fontSize: 56, color: c }}>{a}</span>
            <span style={{ fontFamily: F.song, fontSize: 32, color: C.ink, letterSpacing: 4 }}>{b}</span>
          </div>
        </Ink>
      ))}
    </div>
  </AbsoluteFill>
);

const ROWS = [
  ["农轻重协调发展", "新型工业化 · 乡村振兴"],
  ["沿海与内地", "区域协调发展"],
  ["经济与国防", "军民融合发展"],
  ["国家、集体与个人", "共同富裕"],
];

const Timeline: React.FC<{ t4: number }> = ({ t4 }) => {
  const f = useCurrentFrame();
  const axis = ramp(f, 4, 40, 0, 1, io);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={330} y1={200} x2={330 + 1260 * axis} y2={200} stroke={C.ink} strokeWidth={2} />
        <circle cx={330} cy={200} r={9} fill={C.ink} />
        <circle cx={1590} cy={200} r={9} fill={C.red} opacity={axis > 0.98 ? 1 : 0} />
      </svg>
      <div style={{ position: "absolute", left: 330, top: 222, translate: "-50% 0", fontFamily: F.heavy, fontSize: 40, color: C.ink }}>1956</div>
      <div style={{ position: "absolute", left: 1590, top: 222, translate: "-50% 0", fontFamily: F.heavy, fontSize: 40, color: C.red, opacity: axis }}>2026</div>
      <div style={{ position: "absolute", left: 960, top: 150, translate: "-50% 0", fontFamily: F.kai, fontSize: 36, color: C.gray, letterSpacing: 10, opacity: axis }}>七十年</div>
      {ROWS.map(([a, b], i) => {
        const at = i < 2 ? 40 + i * 70 : t4 + 10 + (i - 2) * 60;
        const k = ramp(f, at + 10, at + 46, 0, 1, io);
        const y = 360 + i * 130;
        return (
          <div key={i}>
            <Ink at={at} style={{ position: "absolute", left: 230, top: y - 30, width: 420, textAlign: "right" }}>
              <div style={{ fontFamily: F.song, fontSize: 42, color: C.ink, letterSpacing: 4, whiteSpace: "nowrap" }}>{a}</div>
            </Ink>
            <svg width={560} height={40} style={{ position: "absolute", left: 680, top: y - 18 }}>
              <line x1={10} y1={20} x2={10 + 520 * k} y2={20} stroke={C.red} strokeWidth={2.5} strokeDasharray="2 0" />
              <circle cx={10} cy={20} r={7} fill={C.ink} opacity={ramp(f, at, at + 10)} />
              <path d="M530,20 l-18,-10 l0,20 Z" fill={C.red} opacity={k > 0.98 ? 1 : 0} />
            </svg>
            <Ink at={at + 40} style={{ position: "absolute", left: 1270, top: y - 32 }}>
              <div style={{ fontFamily: F.heavy, fontSize: 46, color: C.red, letterSpacing: 4, whiteSpace: "nowrap" }}>{b}</div>
            </Ink>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const QS = [
  { t: "数字化治理时代，央地权责的尺度？", x: 170, y: 220, r: -2 },
  { t: "技术迭代极快，国防的“时间窗口”？", x: 1000, y: 320, r: 1.5 },
  { t: "内地承接产业转移，如何形成内生动力？", x: 230, y: 560, r: 1 },
  { t: "市场条件下，如何识别隐蔽的民族歧视？", x: 960, y: 690, r: -1.5 },
];

const Questions: React.FC = () => (
  <AbsoluteFill>
    {QS.map((q, i) => (
      <div key={i} style={{ position: "absolute", left: q.x, top: q.y, rotate: `${q.r}deg` }}>
        <Write at={6 + i * 18} d={26}>
          <div style={{ fontFamily: F.kai, fontSize: 46, color: C.red, letterSpacing: 2, whiteSpace: "nowrap" }}>{q.t}</div>
        </Write>
      </div>
    ))}
  </AbsoluteFill>
);

export const S7: React.FC = () => {
  const L = S.lines.map((_, i) => B(i));
  const end = (i: number) => (L[i + 1]?.a ?? S.dur) + 6;
  const len = (a: number, b: number) => end(b) - L[a].a + 6;
  return (
    <AbsoluteFill>
      <Fade a={0} b={end(0)}>
        <Level />
      </Fade>
      <Fade a={L[1].a - 6} b={end(1)}>
        <PoLi />
      </Fade>
      <Fade a={L[2].a - 6} b={end(2)}>
        <ScanFocus marks={[{ page: "p34", find: "这些矛盾在实践中是否能完全处理好，也要准备两种可能性" }]} at={30} dur={L[2].d - 50} len={len(2, 2)} seed={101} />
      </Fade>
      <Fade a={L[3].a - 6} b={end(4)}>
        <Timeline t4={L[4].a - L[3].a + 6} />
      </Fade>
      <Fade a={L[5].a - 6} b={end(5)}>
        <Questions />
      </Fade>
      <Fade a={L[6].a - 6} b={end(6)} fi={18} fo={18}>
        <FrameSeq shot="desk_close" rate={330 / len(6, 6)} />
      </Fade>
      <Fade a={L[7].a - 6} b={S.dur} fo={20}>
        <ScanFocus marks={[{ page: "p34", find: "道路总是曲折的，前途总是光明" }]} at={10} dur={L[7].d - 24} len={S.dur - L[7].a + 6} seed={103} />
      </Fade>
    </AbsoluteFill>
  );
};
