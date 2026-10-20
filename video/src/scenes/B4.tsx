import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { ScanFocus } from "../lib/ScanFocus";
import { Strips } from "../lib/Strips";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { ChapterCard, Fade, Ink, Note, RunningHead, Write } from "../lib/ui";

const S = scene("B4");
const B = beats(S);

/** a vane that turns with every wind */
const Vane: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const t1 = len * 0.28;
  const t2 = len * 0.55;
  const t3 = len * 0.8;
  // wind source angle (deg, 0 = north/up, 270 = west/left)
  const wind = interpolate(f, [0, t1, t1 + 14, t2, t2 + 14, t3, t3 + 14, len], [0, 0, 270, 270, 360, 360, 360 + 270 + 180, 360 + 270 + 180], { extrapolateRight: "clamp", easing: io });
  const north = f < t1 || (f > t2 + 7 && f < t3);
  const cx = 960;
  const cy = 500;
  const streaks = Array.from({ length: 14 }, (_, i) => i);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <g transform={`rotate(${wind} ${cx} ${cy})`} opacity={0.5}>
          {streaks.map((i) => {
            const p = ((f * 9 + i * 97) % 900) - 450;
            const x = cx - 420 + ((i * 131) % 840);
            return <line key={i} x1={x} y1={cy + p - 60} x2={x} y2={cy + p + 40} stroke={C.gray} strokeWidth={2} strokeLinecap="round" />;
          })}
        </g>
        <circle cx={cx} cy={cy} r={230} fill="none" stroke={C.ink} strokeWidth={2} />
        <circle cx={cx} cy={cy} r={8} fill={C.ink} />
        {[
          ["北", 0, -270],
          ["东", 270, 0],
          ["南", 0, 270],
          ["西", -270, 0],
        ].map(([t, dx, dy]) => (
          <text key={t as string} x={cx + (dx as number)} y={cy + (dy as number) + 16} textAnchor="middle" fontFamily="STSong" fontSize={44} fill={C.ink}>
            {t}
          </text>
        ))}
        <g transform={`rotate(${wind} ${cx} ${cy})`}>
          <path d={`M${cx},${cy - 200} L${cx - 26},${cy - 140} L${cx - 8},${cy - 140} L${cx - 8},${cy + 120} L${cx - 50},${cy + 190} L${cx + 50},${cy + 190} L${cx + 8},${cy + 120} L${cx + 8},${cy - 140} L${cx + 26},${cy - 140} Z`} fill={C.red} />
        </g>
      </svg>
      <div style={{ position: "absolute", left: 1330, top: 440, fontFamily: F.heavy, fontSize: 64, letterSpacing: 8, color: C.ink, opacity: f > 10 && f < t3 ? 1 : 0 }}>{north ? "北风派" : "西风派"}</div>
      <Ink at={t3 + 20}>
        <div style={{ position: "absolute", top: 820, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 6 }}>自己毫无主见，往往由一个极端走到另一个极端</div>
      </Ink>
    </AbsoluteFill>
  );
};

const TwoPoints: React.FC = () => {
  const f = useCurrentFrame();
  const k = ramp(f, 30, 70, 0, 1, io);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={960 - 360 * k} y1={480} x2={960 + 360 * k} y2={480} stroke={C.ink} strokeWidth={3} />
        <circle cx={960 - 360 * k} cy={480} r={30 - 6 * k} fill={C.ink} />
        <circle cx={960 + 360 * k} cy={480} r={24 * k} fill={C.red} />
      </svg>
      <Ink at={4}>
        <div style={{ position: "absolute", top: 230, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 62, color: C.ink, letterSpacing: 14 }}>
          两点<span style={{ color: C.gray, fontFamily: F.song, fontSize: 48 }}>而不是</span>一点
        </div>
      </Ink>
      <Ink at={70} style={{ position: "absolute", left: 600, top: 540, translate: "-50% 0" }}>
        <div style={{ fontFamily: F.song, fontSize: 44, color: C.ink, letterSpacing: 8 }}>优点</div>
      </Ink>
      <Ink at={78} style={{ position: "absolute", left: 1320, top: 540, translate: "-50% 0" }}>
        <div style={{ fontFamily: F.song, fontSize: 44, color: C.red, letterSpacing: 8 }}>缺点</div>
      </Ink>
      <Ink at={90}>
        <div style={{ position: "absolute", top: 700, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 48, color: C.red, letterSpacing: 10 }}>“一万年都有两点”</div>
      </Ink>
    </AbsoluteFill>
  );
};

const BlankSheet: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const words = "正好写字";
  const at0 = Math.max(40, len - 110);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <Ink at={0}>
        <div style={{ fontFamily: F.song, fontSize: 38, color: C.gray, letterSpacing: 12, marginBottom: 36, textAlign: "center" }}>
          一为“<span style={{ color: C.ink }}>穷</span>”　二为“<span style={{ color: C.ink }}>白</span>”
        </div>
      </Ink>
      <div style={{ width: 1000, height: 520, background: "#F8F4EC", boxShadow: "0 18px 50px rgba(28,26,23,0.16), 0 2px 6px rgba(28,26,23,0.1)", opacity: ramp(f, 8, 30), rotate: "-1deg", display: "flex", justifyContent: "center", alignItems: "center", gap: 10 }}>
        {[...words].map((c, i) => (
          <Write key={i} at={at0 + i * 16} d={16}>
            <div style={{ fontFamily: F.kai, fontSize: 170, color: C.ink, lineHeight: 1, textShadow: "0 0 1px rgba(28,26,23,0.6)" }}>{c}</div>
          </Write>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Chain: React.FC = () => {
  const steps = [
    ["开源交流", "学习原理"],
    ["本土实践", "检验方案"],
    ["自主创新", "变成自己的力量"],
  ];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 170, top: 250, display: "flex", flexDirection: "column", gap: 60 }}>
        {steps.map(([a, b], i) => (
          <Ink key={i} at={10 + i * 40}>
            <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
              <div style={{ width: 260, fontFamily: F.heavy, fontSize: 50, color: i === 2 ? C.red : C.ink, letterSpacing: 6, textAlign: "right" }}>{a}</div>
              <div style={{ width: 80, height: 2, background: C.ink }} />
              <div style={{ fontFamily: F.song, fontSize: 44, color: C.gray, letterSpacing: 6 }}>{b}</div>
            </div>
          </Ink>
        ))}
      </div>
      <Note at={150} label="研读联系 · 人工智能" lines={["学原理，不照搬路线；", "在交流中学习，", "在实践中检验。"]} x={1240} y={300} w={600} size={46} perLine={36} />
    </AbsoluteFill>
  );
};

export const B4: React.FC = () => {
  const L = S.lines.map((_, i) => B(i));
  const c0 = L[0].a;
  const f = useCurrentFrame();
  const end = (i: number) => (L[i + 1]?.a ?? S.dur) + 6;
  const len = (a: number, b: number) => end(b) - L[a].a + 6;
  return (
    <AbsoluteFill>
      <Fade a={0} b={c0 + 4} fi={10} fo={10}>
        <ChapterCard {...S.card!} len={c0 + 4} />
      </Fade>
      <Fade a={L[0].a - 6} b={end(0)}>
        <ScanFocus marks={[{ page: "p30", find: "我们提出向外国学习的口号，我想是提得对的" }, { page: "p30", find: "就是要把戏台上的那个架子放下来" }]} at={14} dur={L[0].d - 30} len={len(0, 0)} fitH={560} seed={91} />
      </Fade>
      <Fade a={L[1].a - 6} b={end(1)}>
        <Strips
          items={[{ page: "p30", find: "一切民族、一切国家的长处都要" }, { page: "p30", find: "必须有分析有批判地学，不能盲目" }, { page: "p31", find: "地学，不能一切照抄，机械搬运" }]}
          at={14}
          per={Math.round((L[1].d - 20) / 3)}
          gap={30}
          seed={93}
        />
      </Fade>
      <Fade a={L[2].a - 6} b={end(2)}>
        <Vane len={len(2, 2)} />
      </Fade>
      <Fade a={L[3].a - 6} b={end(3)}>
        <TwoPoints />
      </Fade>
      <Fade a={L[4].a - 6} b={end(4)}>
        <BlankSheet len={len(4, 4)} />
      </Fade>
      <Fade a={L[5].a - 6} b={end(5)}>
        <ScanFocus marks={[{ page: "p34", find: "还应当向人家学习。一万年都要学习嘛" }]} at={14} dur={L[5].d - 30} len={len(5, 5)} seed={95} />
      </Fade>
      <Fade a={L[6].a - 6} b={S.dur}>
        <Chain />
      </Fade>
      {f > c0 - 10 && <RunningHead block="肆 · 独立自主与对外开放" rel="十　中国和外国的关系" at={c0 - 10} />}
    </AbsoluteFill>
  );
};
