import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { Fade, Ink } from "../lib/ui";

const S = scene("S0");
const B = beats(S);

const STRIPS = [
  { no: "三", tag: "经济建设和国防建设", page: "p13", find: "你对原子弹是真正想要、十分想要，还是只有几分想", circle: "十分想要", line: 1 },
  { no: "一", tag: "重工业和轻工业、农业", page: "p10", find: "你如果是真想，或者想得厉害，那你就要注重", circle: "真想", line: 3 },
  { no: "二", tag: "沿海工业和内地工业", page: "p12", find: "如果是真想，不是假想，就必须更多地利用和发展沿海工业", circle: "真想", line: 4 },
];

const GOALS = [
  ["想要原子弹", "先多搞经济建设"],
  ["想要重工业", "先多发展农业、轻工业"],
  ["想要内地工业", "先用好沿海老底子"],
];

const Strips: React.FC<{ stripsAt: number }> = ({ stripsAt }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ padding: "96px 140px 0", flexDirection: "column", gap: 26 }}>
      {STRIPS.map((s, i) => {
        const appear = i === 0 ? 0 : B(s.line).a - 4 - stripsAt;
        const k = ramp(f, appear, appear + 22);
        return (
          <div key={i} style={{ opacity: k, translate: `0 ${(1 - k) * 24}px`, display: "flex", alignItems: "center", gap: 44 }}>
            <div style={{ width: 330, textAlign: "right" }}>
              <div style={{ fontFamily: F.heavy, fontSize: 64, color: C.red, lineHeight: 1 }}>{s.no}</div>
              <div style={{ fontFamily: F.song, fontSize: 28, color: C.gray, letterSpacing: 2, marginTop: 12, whiteSpace: "nowrap" }}>{s.tag}</div>
            </div>
            <div style={{ position: "relative", width: 1240, height: 236, borderTop: `1px solid ${C.faint}`, borderBottom: `1px solid ${C.faint}` }}>
              <ScanFocus marks={[{ page: s.page, find: s.find, circle: s.circle }]} w={1240} h={236} cy={118} at={appear + 8} dur={34} len={300} fitW={1200} fitH={200} maxScale={0.6} dim={false} seed={20 + i} />
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const Goals: React.FC<{ t6: number }> = ({ t6 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 54, opacity: 1 - ramp(f, t6 + 20, t6 + 50, 0, 1, io) }}>
        <div style={{ display: "flex", fontFamily: F.kai, fontSize: 34, letterSpacing: 6 }}>
          <Ink at={40} style={{ width: 560, textAlign: "right", color: C.red }}>
            先照顾好那一头
          </Ink>
          <div style={{ width: 420 }} />
          <Ink at={48} style={{ color: C.gray }}>
            要抓住这一头
          </Ink>
        </div>
        {GOALS.map(([goal, path], i) => {
          const at = 8 + i * 10;
          const k = ramp(f, at + 16, at + 46, 0, 1, io);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center" }}>
              <Ink at={at} style={{ width: 560, textAlign: "right", fontFamily: F.heavy, fontSize: 52, color: C.ink, letterSpacing: 4 }}>
                {path}
              </Ink>
              <svg width={360} height={80} style={{ margin: "0 30px" }}>
                <line x1={20} y1={40} x2={20 + 320 * k} y2={40} stroke={C.ink} strokeWidth={2.5} />
                <circle cx={20} cy={40} r={11} fill={C.red} opacity={ramp(f, at, at + 14)} />
                <circle cx={340} cy={40} r={11} fill="none" stroke={C.ink} strokeWidth={2.5} opacity={ramp(f, at + 36, at + 50)} />
              </svg>
              <Ink at={at + 30} style={{ width: 380, fontFamily: F.song, fontSize: 52, color: C.gray, letterSpacing: 4 }}>
                {goal}
              </Ink>
            </div>
          );
        })}
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
        {(() => {
          const k = ramp(f, t6 + 34, t6 + 80, 0, 1, io);
          const L = 80 + 1500 * k;
          return (
            <g opacity={ramp(f, t6 + 30, t6 + 44)}>
              <line x1={960 - L / 2} y1={470} x2={960 + L / 2} y2={470} stroke={C.ink} strokeWidth={2.5} />
              <circle cx={960 - L / 2} cy={470} r={14} fill={C.red} />
              <circle cx={960 + L / 2} cy={470} r={14} fill={C.paper} stroke={C.ink} strokeWidth={2.5} />
            </g>
          );
        })()}
      </svg>
    </AbsoluteFill>
  );
};

export const S0: React.FC = () => {
  const b1 = B(1);
  const b2 = B(2);
  const b5 = B(5);
  const b6 = B(6);
  const stripsAt = B(3).a - 6;
  return (
    <AbsoluteFill>
      <Fade a={0} b={stripsAt + 10} fi={30}>
        <ScanFocus
          marks={[{ page: "p13", find: "你对原子弹是真正想要、十分想要，还是只有几分想，没有十分想呢" }, { page: "p13", find: "你就降低军政费用的比重，多搞经济建设" }]}
          at={b1.a + 6}
          dur={b2.b - b1.a - 30}
          len={stripsAt + 10}
          maxScale={1.05}
          fitH={430}
          seed={3}
        />
      </Fade>
      <Fade a={stripsAt} b={b5.a + 18}>
        <Strips stripsAt={stripsAt} />
      </Fade>
      <Fade a={b5.a} b={S.dur} fo={10}>
        <Goals t6={b6.a - b5.a} />
      </Fade>
    </AbsoluteFill>
  );
};
