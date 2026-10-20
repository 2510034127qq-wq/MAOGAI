import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { Fade, FrameSeq, Ink } from "../lib/ui";

const S = scene("S1");
const B = beats(S);

const Year: React.FC = () => {
  const f = useCurrentFrame();
  const b = B(0);
  const q = ramp(f, b.a + 70, b.a + 100, 0, 1, io);
  const per = 2 * Math.PI * 62;
  return (
    <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", padding: "0 200px", gap: 110 }}>
      <Ink at={4} d={30} rise={0}>
        <div style={{ fontFamily: F.heavy, fontSize: 280, color: C.ink, letterSpacing: 6, lineHeight: 1 }}>1956</div>
      </Ink>
      <div style={{ display: "flex", flexDirection: "column", gap: 30 }}>
        {["社会主义改造　即将基本完成", "第一个五年计划　正在实施"].map((t, i) => (
          <Ink key={i} at={14 + i * 16}>
            <div style={{ fontFamily: F.song, fontSize: 44, color: C.gray, letterSpacing: 6, display: "flex", alignItems: "center", gap: 22 }}>
              <span style={{ width: 12, height: 12, background: C.red, display: "inline-block" }} />
              {t}
            </div>
          </Ink>
        ))}
        <Ink at={b.a + 56}>
          <div style={{ fontFamily: F.heavy, fontSize: 70, color: C.ink, letterSpacing: 8, marginTop: 40, position: "relative" }}>
            怎样建设社会主义<span style={{ color: C.red }}>？</span>
            <svg width={160} height={160} style={{ position: "absolute", right: -18, top: -34, overflow: "visible" }}>
              <circle cx={80} cy={80} r={62} fill="none" stroke={C.red} strokeWidth={4} strokeDasharray={per} strokeDashoffset={per * (1 - q)} transform="rotate(-100 80 80)" opacity={0.85} />
            </svg>
          </div>
        </Ink>
      </div>
    </AbsoluteFill>
  );
};

const Congress: React.FC = () => {
  const f = useCurrentFrame();
  const b = { ...B(1), a: 4 };
  const crack = ramp(f, b.a + 60, b.a + 84, 0, 1, io);
  const split = ramp(f, b.a + 84, b.a + 110, 0, 1, io);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Ink at={b.a}>
        <div style={{ fontFamily: F.song, fontSize: 40, color: C.red, letterSpacing: 10 }}>一九五六年二月</div>
      </Ink>
      <Ink at={b.a + 10}>
        <div style={{ fontFamily: F.song, fontSize: 52, color: C.ink, letterSpacing: 10, marginTop: 20 }}>苏联共产党第二十次代表大会</div>
      </Ink>
      <div style={{ position: "relative", marginTop: 70, height: 220, width: 900 }}>
        {[0, 1].map((side) => (
          <div
            key={side}
            style={{
              position: "absolute",
              inset: 0,
              textAlign: "center",
              fontFamily: F.heavy,
              fontSize: 190,
              letterSpacing: 30,
              color: C.ink,
              opacity: ramp(f, b.a + 26, b.a + 50) * (1 - 0.45 * split),
              clipPath: side ? "polygon(52% 0, 100% 0, 100% 100%, 47% 100%, 50% 60%, 46% 38%)" : "polygon(0 0, 52% 0, 46% 38%, 50% 60%, 47% 100%, 0 100%)",
              translate: `${(side ? 1 : -1) * 18 * split}px ${(side ? 1 : -1) * 6 * split}px`,
              rotate: `${(side ? 1 : -1) * 1.5 * split}deg`,
            }}
          >
            苏联模式
          </div>
        ))}
        <svg width={900} height={220} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          <path d="M468,-10 L414,84 L450,132 L423,230" stroke={C.red} strokeWidth={4} fill="none" strokeDasharray={420} strokeDashoffset={420 * (1 - crack)} opacity={1 - split} />
        </svg>
      </div>
      <Ink at={b.a + 100}>
        <div style={{ fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 10, marginTop: 40 }}>打破迷信</div>
      </Ink>
    </AbsoluteFill>
  );
};

const Cards: React.FC = () => {
  const f = useCurrentFrame();
  const b = { ...B(2), a: 4 };
  const span = b.d - 50;
  const cols = 9;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Ink at={b.a}>
        <div style={{ fontFamily: F.song, fontSize: 42, color: C.gray, letterSpacing: 8, marginBottom: 46 }}>工业 · 农业 · 运输业 · 商业 · 财政 ……</div>
      </Ink>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 150px)`, gap: 18 }}>
        {Array.from({ length: 34 }, (_, i) => {
          const at = b.a + 8 + (i / 34) * span;
          const k = ramp(f, at, at + 14);
          return (
            <div
              key={i}
              style={{
                height: 92,
                border: `1.5px solid ${C.ink}`,
                background: C.paperHi,
                opacity: k,
                translate: `0 ${(1 - k) * -26}px`,
                rotate: `${((i * 37) % 7) - 3}deg`,
                boxShadow: "2px 3px 0 rgba(28,26,23,0.12)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                padding: "10px 12px",
              }}
            >
              <div style={{ height: 2, background: C.red, width: 40 }} />
              <div style={{ fontFamily: F.serif, fontSize: 30, color: C.ink, textAlign: "right" }}>{String(i + 1).padStart(2, "0")}</div>
            </div>
          );
        })}
      </div>
      <Ink at={b.a + span + 10}>
        <div style={{ fontFamily: F.heavy, fontSize: 64, color: C.ink, letterSpacing: 12, marginTop: 56 }}>
          三十四个部门的汇报 <span style={{ fontFamily: F.song, fontSize: 40, color: C.gray, letterSpacing: 6 }}>· 两个多月</span>
        </div>
      </Ink>
    </AbsoluteFill>
  );
};

export const S1: React.FC = () => {
  const b0 = B(0);
  const b1 = B(1);
  const b2 = B(2);
  const b3 = B(3);
  const b4 = B(4);
  const b5 = B(5);
  return (
    <AbsoluteFill>
      <Fade a={0} b={b1.a}>
        <Year />
      </Fade>
      <Fade a={b1.a - 4} b={b2.a}>
        <Congress />
      </Fade>
      <Fade a={b2.a - 4} b={b3.a + 4}>
        <Cards />
      </Fade>
      <Fade a={b3.a - 4} b={b4.a + 10} fi={16} fo={18}>
        <FrameSeq shot="desk_open" rate={180 / (b4.a - b3.a + 10)} />
      </Fade>
      <Fade a={b4.a - 8} b={b5.a + 6}>
        <ScanFocus marks={[{ page: "p07", find: "要把国内外一切积极因素调动起来，为社会主义事业服务" }]} establish at={b4.a - b4.a + 46} dur={b4.d - 60} len={b5.a - b4.a + 14} seed={41} />
      </Fade>
      <Fade a={b5.a - 6} b={S.dur} fo={12}>
        <ScanFocus marks={[{ page: "p08", find: "他们走过的弯路，你还想走", circle: "你还想走" }]} at={14} dur={b5.d - 50} len={S.dur - b5.a} seed={43} />
      </Fade>
      {/* timing anchor so unused-vars lint stays quiet */}
      <span style={{ display: "none" }}>{b0.a}</span>
    </AbsoluteFill>
  );
};
