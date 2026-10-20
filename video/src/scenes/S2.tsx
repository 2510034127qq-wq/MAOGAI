import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { GROUPS, PAIRS, PairRow } from "../lib/pairs";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { Fade, FrameSeq, Ink } from "../lib/ui";

const S = scene("S2");
const B = beats(S);

const TOC = ["重工业和轻工业、农业的关系", "沿海工业和内地工业的关系", "经济建设和国防建设的关系", "国家、生产单位和生产者个人的关系", "中央和地方的关系", "汉族和少数民族的关系", "党和非党的关系", "革命和反革命的关系", "是非关系", "中国和外国的关系"];

/** correct handling is neither deleting one end nor splitting evenly */
const Demo: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const h = len / 2;
  const erase = ramp(f, 16, 40, 0, 1, io) * (1 - ramp(f, h - 10, h + 6, 0, 1, io));
  const even = ramp(f, h + 6, h + 30, 0, 1, io);
  const rL = interpolate(even, [0, 1], [30, 22]);
  const rR = interpolate(even, [0, 1], [16, 22]);
  const cross = (at: number) => ramp(f, at, at + 14, 0, 1, io);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={560} y1={470} x2={1360 - 800 * erase * 0.0} y2={470} stroke={C.ink} strokeWidth={3} opacity={1 - erase * 0.75} />
        <circle cx={560} cy={470} r={rL} fill={C.red} />
        <circle cx={1360} cy={470} r={rR} fill={C.paper} stroke={C.ink} strokeWidth={3} opacity={1 - erase} />
        {/* strike marks */}
        <g opacity={f < h ? cross(40) : 0} stroke={C.red} strokeWidth={6} strokeLinecap="round">
          <line x1={1320} y1={430} x2={1400} y2={510} />
          <line x1={1400} y1={430} x2={1320} y2={510} />
        </g>
        <g opacity={f >= h ? cross(h + 34) : 0} stroke={C.red} strokeWidth={6} strokeLinecap="round">
          <line x1={920} y1={430} x2={1000} y2={510} />
          <line x1={1000} y1={430} x2={920} y2={510} />
        </g>
      </svg>
      <div style={{ position: "absolute", top: 600, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 56, color: C.red, letterSpacing: 12 }}>
        <span style={{ opacity: f < h ? ramp(f, 40, 56) : 0 }}>不是取消一端</span>
        <span style={{ position: "absolute", left: 0, right: 0, opacity: f >= h ? ramp(f, h + 34, h + 50) : 0 }}>也不是平均用力</span>
      </div>
    </AbsoluteFill>
  );
};

const Stamp: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  const k = ramp(f, at, at + 12);
  return (
    <div
      style={{
        position: "absolute",
        right: 150,
        bottom: 170,
        border: `5px solid ${C.red}`,
        padding: "10px 26px",
        fontFamily: F.heavy,
        fontSize: 76,
        letterSpacing: 14,
        color: C.red,
        opacity: k * 0.92,
        scale: String(1.3 - 0.3 * k),
        rotate: "-3deg",
        background: "rgba(237,229,212,0.5)",
      }}
    >
      统筹兼顾
    </div>
  );
};

/** ten pairs as a list, then regrouped into the report's four blocks */
const Regroup: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const t = ramp(f, 40, Math.min(len - 40, 120), 0, 1, io);
  const colX = [250, 720, 1190, 1660];
  return (
    <AbsoluteFill>
      {PAIRS.map((_, i) => {
        const g = GROUPS.findIndex((G) => G.idx.includes(i));
        const pos = GROUPS[g].idx.indexOf(i);
        const listX = 960;
        const listY = 150 + i * 66;
        const gx = colX[g];
        const gy = 430 + pos * 82;
        const stagger = ramp(f, 40 + i * 4, 100 + i * 4, 0, 1, io);
        const x = listX + (gx - listX) * stagger;
        const y = listY + (gy - listY) * stagger;
        const sc = 1 - 0.42 * stagger;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y, translate: "-50% -50%", scale: String(sc), opacity: ramp(f, i * 2, i * 2 + 14) }}>
            <PairRow i={i} size={40} lineW={200} />
          </div>
        );
      })}
      {GROUPS.map((G, g) => {
        const k = ramp(f, 110 + g * 8, 136 + g * 8);
        return (
          <div key={g} style={{ position: "absolute", left: colX[g], top: 250, translate: "-50% 0", textAlign: "center", opacity: k * (t > 0.5 ? 1 : 0) }}>
            <div style={{ width: 96, height: 96, margin: "0 auto", background: C.red, display: "flex", justifyContent: "center", alignItems: "center" }}>
              <span style={{ fontFamily: F.heavy, fontSize: 66, color: C.paperHi }}>{G.no}</span>
            </div>
            <div style={{ fontFamily: F.heavy, fontSize: 36, color: C.ink, letterSpacing: 4, marginTop: 20, whiteSpace: "nowrap" }}>{G.title}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export const S2: React.FC = () => {
  const b0 = B(0);
  const b1 = B(1);
  const b2 = B(2);
  const b3 = B(3);
  const b4 = B(4);
  const b5 = B(5);
  return (
    <AbsoluteFill>
      <Fade a={0} b={b1.a + 4}>
        <ScanFocus marks={TOC.map((t) => ({ page: "p06", find: t }))} establish at={30} dur={b0.b - 30} len={b1.a + 4} fitH={760} fitW={1300} maxScale={1.1} cy={470} dim={false} seed={51} />
      </Fade>
      <Fade a={b1.a - 4} b={b2.a + 4}>
        <ScanFocus marks={[{ page: "p34", find: "这十种关系，都是矛盾。世界是由矛盾组成的。没有矛盾就没有世界" }]} at={18} dur={b1.d - 40} len={b2.a - b1.a + 8} seed={53} />
      </Fade>
      <Fade a={b2.a - 4} b={b3.a + 2}>
        <Demo len={b3.a - b2.a + 6} />
      </Fade>
      <Fade a={b3.a - 6} b={b5.a + 6} fi={10}>
        <FrameSeq shot="steelyard_balance" />
        <Stamp at={b4.a - b3.a + 30} />
      </Fade>
      <Fade a={b5.a - 6} b={S.dur} fo={16}>
        <Regroup len={S.dur - b5.a + 6} />
        <Ink at={b5.d - 20}>
          <div style={{ position: "absolute", top: 120, width: "100%", textAlign: "center", fontFamily: F.song, fontSize: 32, color: C.gray, letterSpacing: 8 }}>十位组员 · 各领一条 · 重组为四个板块</div>
        </Ink>
      </Fade>
    </AbsoluteFill>
  );
};
