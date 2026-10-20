import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ScanFocus } from "../lib/ScanFocus";
import { C, F, io, ramp } from "../lib/theme";
import { beats, scene } from "../lib/timeline";
import { ChapterCard, Fade, Ink, Note, Plate, RunningHead, Write } from "../lib/ui";

const S = scene("B2");
const B = beats(S);
const REL = ["四　国家、生产单位和生产者个人的关系", "五　中央和地方的关系"];

/** three parties held together; pulling one corner strains the whole */
const Triangle: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const pull = ramp(f, 50, 80, 0, 1, io) * (1 - ramp(f, len - 50, len - 20, 0, 1, io));
  const P = [
    { x: 960, y: 250, t: "国家" },
    { x: 620 - 260 * pull, y: 730 + 40 * pull, t: "生产单位", s: "工厂 · 合作社" },
    { x: 1300, y: 730, t: "生产者个人", s: "工人 · 农民" },
  ];
  const k = ramp(f, 4, 34, 0, 1, io);
  const strain = pull > 0.05;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {[
          [0, 1],
          [1, 2],
          [2, 0],
        ].map(([a, b], i) => (
          <line key={i} x1={P[a].x} y1={P[a].y} x2={P[a].x + (P[b].x - P[a].x) * k} y2={P[a].y + (P[b].y - P[a].y) * k} stroke={strain && (a === 1 || b === 1) ? C.red : C.ink} strokeWidth={strain && (a === 1 || b === 1) ? 3.5 : 2.5} strokeDasharray={strain && (a === 1 || b === 1) ? "10 8" : "none"} />
        ))}
        {P.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={16} fill={i === 0 ? C.ink : C.paper} stroke={C.ink} strokeWidth={3} />
        ))}
      </svg>
      {P.map((p, i) => (
        <div key={i} style={{ position: "absolute", left: p.x, top: p.y + (i === 0 ? -100 : 34), translate: "-50% 0", textAlign: "center", whiteSpace: "nowrap" }}>
          <div style={{ fontFamily: F.heavy, fontSize: 50, color: C.ink, letterSpacing: 6 }}>{p.t}</div>
          {p.s && <div style={{ fontFamily: F.song, fontSize: 30, color: C.gray, letterSpacing: 4, marginTop: 8 }}>{p.s}</div>}
        </div>
      ))}
      <Ink at={80}>
        <div style={{ position: "absolute", top: 520, width: "100%", textAlign: "center" }}>
          <span style={{ fontFamily: F.kai, fontSize: 54, color: C.red, letterSpacing: 10, background: C.paper, padding: "4px 24px", boxShadow: `0 0 24px 12px ${C.paper}` }}>不能只顾一头</span>
        </div>
      </Ink>
    </AbsoluteFill>
  );
};

const ROWS = [
  ["一九五四年", "部分地区水灾减产", "多购七十亿斤", "人人谈粮食，户户谈统销"],
  ["一九五五年", "“三定”：定产 定购 定销；丰收", "少购七十亿斤", "农民手里多了二百多亿斤"],
];
const COLS = [230, 520, 300, 470];

const Ledger: React.FC<{ rows: number; fullFirst?: boolean; len: number }> = ({ rows, fullFirst, len }) => {
  const f = useCurrentFrame();
  const x0 = 200;
  const heads = ["年份", "情况", "购粮", "结果"];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x0, top: 210, width: 1520, height: 560, background: C.paperHi, boxShadow: "0 8px 30px rgba(28,26,23,0.12)", opacity: ramp(f, 0, 14) }}>
        {[0, 1, 2, 3, 4].map((r) => (
          <div key={r} style={{ position: "absolute", left: 0, right: 0, top: 110 + r * 110, height: 1, background: "#B9C3C9" }} />
        ))}
        <div style={{ position: "absolute", left: 60, top: 0, bottom: 0, width: 1.5, background: C.red }} />
        <div style={{ position: "absolute", left: 66, top: 0, bottom: 0, width: 1.5, background: C.red }} />
        {heads.map((h, i) => (
          <div key={h} style={{ position: "absolute", top: 50, left: 90 + COLS.slice(0, i).reduce((a, b) => a + b, 0), fontFamily: F.song, fontSize: 32, color: C.gray, letterSpacing: 8 }}>
            {h}
          </div>
        ))}
        {ROWS.slice(0, rows).map((row, r) =>
          row.map((cell, c) => {
            const isNew = r === rows - 1 && !(r === 0 && fullFirst);
            const at = isNew ? 14 + c * Math.max(18, (len - 60) / 5) : -100;
            if (r === 0 && c === 3 && !fullFirst && rows === 1) return null;
            const red = c === 2 || (r === 1 && c === 3);
            return (
              <Write key={`${r}${c}`} at={at} d={22} style={{ position: "absolute", top: 140 + r * 150, left: 90 + COLS.slice(0, c).reduce((a, b) => a + b, 0), width: COLS[c] - 20 }}>
                <div style={{ fontFamily: F.kai, fontSize: r === 1 && c === 3 ? 46 : 40, color: red ? C.red : C.ink, lineHeight: 1.35 }}>{cell}</div>
              </Write>
            );
          }),
        )}
      </div>
    </AbsoluteFill>
  );
};

/** 开会 / 散会: unity and independence */
const Meeting: React.FC<{ t7: number; len: number }> = ({ t7, len }) => {
  const f = useCurrentFrame();
  const disperse = ramp(f, 70, 120, 0, 1, io) * (1 - ramp(f, t7 - 10, t7 + 40, 0, 1, io));
  const wobble = ramp(f, t7 + 30, t7 + 70);
  const cols = 12;
  const rows = 6;
  const dots = Array.from({ length: cols * rows }, (_, i) => i);
  const tables = [
    { x: 1420, y: 430 },
    { x: 1580, y: 620 },
    { x: 1360, y: 700 },
  ];
  const groupOf = (i: number) => (i * 7) % 3;
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {tables.map((t, i) => (
          <circle key={i} cx={t.x} cy={t.y} r={46} fill="none" stroke={C.faint} strokeWidth={2} opacity={disperse} />
        ))}
        {dots.map((i) => {
          const gx = 960 + ((i % cols) - (cols - 1) / 2) * 66;
          const gy = 520 + (Math.floor(i / cols) - (rows - 1) / 2) * 66;
          const g = groupOf(i);
          const j = Math.floor(i / 3);
          let px = gx;
          let py = gy;
          if (g === 0) {
            const lane = j % 4;
            const phase = ((f / 90 + j * 0.37) % 1) * 1;
            px = 260 + phase * 460;
            py = 360 + lane * 110 + Math.sin(phase * 9 + j) * 14;
          } else if (g === 1) {
            px = 860 + (j % 4) * 70 + (j % 2) * 8;
            py = 380 + Math.floor(j / 4) * 80;
          } else {
            const t = tables[j % 3];
            const a = (j / 8) * Math.PI * 2 + j;
            px = t.x + Math.cos(a) * 66;
            py = t.y + Math.sin(a) * 66;
          }
          const x = gx + (px - gx) * disperse + Math.cos(f / 9 + i) * 7 * wobble;
          const y = gy + (py - gy) * disperse + Math.sin(f / 11 + i * 1.7) * 7 * wobble;
          return <circle key={i} cx={x} cy={y} r={16} fill={g === 1 ? C.red : C.ink} opacity={ramp(f, i * 0.4, i * 0.4 + 10)} />;
        })}
      </svg>
      <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 52, letterSpacing: 10, color: C.ink }}>
        <span style={{ opacity: (1 - disperse) * (1 - wobble) }}>开会 · 统一性</span>
      </div>
      <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 52, letterSpacing: 10, color: C.ink, opacity: wobble }}>统一性和独立性 · 对立的统一</div>
      <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", fontFamily: F.heavy, fontSize: 52, letterSpacing: 10, color: C.ink, opacity: disperse }}>散会 · 独立性</div>
      {[
        ["散步", 490, 820],
        ["读书", 965, 820],
        ["吃饭", 1470, 820],
      ].map(([t, x, y], i) => (
        <div key={i} style={{ position: "absolute", left: x as number, top: y as number, translate: "-50% 0", fontFamily: F.kai, fontSize: 44, color: C.red, letterSpacing: 8, opacity: disperse }}>
          {t}
        </div>
      ))}
      <div style={{ position: "absolute", top: 820, width: "100%", textAlign: "center", opacity: wobble }}>
        <span style={{ fontFamily: F.kai, fontSize: 48, color: C.red, letterSpacing: 8 }}>与统一性相联系的独立性</span>
      </div>
      <span style={{ display: "none" }}>{len}</span>
    </AbsoluteFill>
  );
};

/** dozens of hands reaching into the locality; forms pile up */
const Hands: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const N = 30;
  const box = { x: 760, y: 640, w: 400, h: 200 };
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 260, top: 200, width: 1400, height: 70, background: C.ink, display: "flex", justifyContent: "center", alignItems: "center", opacity: ramp(f, 0, 12) }}>
        <span style={{ fontFamily: F.heavy, fontSize: 40, color: C.paper, letterSpacing: 14 }}>中央各部</span>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: N }, (_, i) => {
          const x0 = 290 + (i / (N - 1)) * 1340;
          const x1 = box.x + 20 + ((i * 53) % 360);
          const at = 10 + i * 2.2;
          const k = ramp(f, at, at + 18, 0, 1, io);
          return <line key={i} x1={x0} y1={270} x2={x0 + (x1 - x0) * k} y2={270 + (box.y - 270) * k} stroke={C.ink} strokeWidth={1.6} opacity={0.75} />;
        })}
      </svg>
      <div style={{ position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h, border: `3px solid ${C.ink}`, background: C.paperHi, display: "flex", justifyContent: "center", alignItems: "flex-end", paddingBottom: 20 }}>
        <span style={{ fontFamily: F.heavy, fontSize: 40, color: C.ink, letterSpacing: 8 }}>地方 · 厅局</span>
      </div>
      {Array.from({ length: 26 }, (_, i) => {
        const at = 60 + i * ((len - 110) / 26);
        const k = ramp(f, at, at + 10);
        const col = i % 6;
        const lvl = Math.floor(i / 6);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: box.x - 70 + col * 92 + (lvl % 2) * 20,
              top: box.y - 34 - lvl * 26 + (1 - k) * -60,
              width: 100,
              height: 64,
              background: "#F7F3EA",
              border: `1.5px solid ${C.gray}`,
              rotate: `${((i * 41) % 15) - 7}deg`,
              opacity: k,
              backgroundImage: `repeating-linear-gradient(0deg, transparent 0 11px, ${C.faint} 11px 12px)`,
            }}
          />
        );
      })}
      <Ink at={len - 60}>
        <div style={{ position: "absolute", left: 1220, top: 700, fontFamily: F.kai, fontSize: 46, color: C.red, letterSpacing: 6, lineHeight: 1.5 }}>
          表报之多
          <br />
          泛滥成灾
        </div>
      </Ink>
    </AbsoluteFill>
  );
};

const Measure: React.FC = () => {
  const f = useCurrentFrame();
  const chain = ["中央", "省 · 市", "地 · 县 · 区 · 乡"];
  return (
    <AbsoluteFill>
      <Ink at={0}>
        <div style={{ position: "absolute", top: 170, width: "100%", textAlign: "center", fontFamily: F.song, fontSize: 36, color: C.gray, letterSpacing: 8 }}>
          前提：<span style={{ color: C.ink }}>巩固中央的统一领导</span>
        </div>
      </Ink>
      {[
        ["可以和应当统一的", "必须统一", 260],
        ["不可以和不应当统一的", "不能强求统一", 1000],
      ].map(([a, b, x], i) => (
        <div key={i} style={{ position: "absolute", left: x as number, top: 290, width: 660, textAlign: "center" }}>
          <Ink at={20 + i * 40}>
            <div style={{ fontFamily: F.song, fontSize: 40, color: C.gray, letterSpacing: 4 }}>{a}</div>
          </Ink>
          <Ink at={34 + i * 40}>
            <div style={{ fontFamily: F.heavy, fontSize: 76, color: i ? C.red : C.ink, letterSpacing: 10, marginTop: 20 }}>{b}</div>
          </Ink>
        </div>
      ))}
      <div style={{ position: "absolute", left: 958, top: 300, width: 2, height: 220, background: C.faint, opacity: ramp(f, 20, 40) }} />
      <div style={{ position: "absolute", top: 640, width: "100%", display: "flex", justifyContent: "center", alignItems: "center", gap: 30 }}>
        {chain.map((c, i) => (
          <React.Fragment key={c}>
            <Ink at={100 + i * 16}>
              <div style={{ fontFamily: F.song, fontSize: 40, color: C.ink, letterSpacing: 6, border: `2px solid ${C.ink}`, padding: "12px 30px" }}>{c}</div>
            </Ink>
            {i < 2 && <div style={{ width: 90, height: 2, background: C.red, opacity: ramp(f, 110 + i * 16, 124 + i * 16) }} />}
          </React.Fragment>
        ))}
      </div>
      <Ink at={150}>
        <div style={{ position: "absolute", top: 760, width: "100%", textAlign: "center", fontFamily: F.kai, fontSize: 40, color: C.red, letterSpacing: 6 }}>层层发挥积极性，“都不能够框得太死”</div>
      </Ink>
    </AbsoluteFill>
  );
};

/** the trap: tighten → dead, loosen → chaos */
const Trap: React.FC = () => {
  const f = useCurrentFrame();
  const items = [
    ["一收", 600, 330],
    ["就死", 900, 330],
    ["一放", 900, 630],
    ["就乱", 600, 630],
  ];
  const k = ramp(f, 10, 60, 0, 1, io);
  return (
    <AbsoluteFill>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <rect x={600} y={330} width={300} height={300} fill="none" stroke={C.faint} strokeWidth={2} strokeDasharray={1200} strokeDashoffset={1200 * (1 - k)} />
        <g stroke={C.red} strokeWidth={6} strokeLinecap="round" opacity={ramp(f, 70, 84)}>
          <line x1={700} y1={430} x2={800} y2={530} />
          <line x1={800} y1={430} x2={700} y2={530} />
        </g>
      </svg>
      {items.map(([t, x, y], i) => (
        <div key={i} style={{ position: "absolute", left: x as number, top: y as number, translate: "-50% -50%", fontFamily: F.heavy, fontSize: 46, color: C.gray, background: C.paper, padding: "4px 10px", opacity: ramp(f, 10 + i * 10, 24 + i * 10) }}>
          {t}
        </div>
      ))}
      <Ink at={60}>
        <div style={{ position: "absolute", left: 750, top: 720, translate: "-50% 0", fontFamily: F.kai, fontSize: 38, color: C.red, whiteSpace: "nowrap" }}>跳出怪圈</div>
      </Ink>
    </AbsoluteFill>
  );
};

export const B2: React.FC = () => {
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
        <Triangle len={len(0, 0)} />
      </Fade>
      <Fade a={L[1].a - 6} b={end(1)}>
        <Ledger rows={1} len={len(1, 1)} />
      </Fade>
      <Fade a={L[2].a - 6} b={end(2)}>
        <ScanFocus marks={[{ page: "p15", find: "几乎人人谈粮食，户户谈统销" }]} at={12} dur={L[2].d - 30} len={len(2, 2)} seed={71} />
      </Fade>
      <Fade a={L[3].a - 6} b={end(3)}>
        <Ledger rows={2} fullFirst len={len(3, 3)} />
      </Fade>
      <Fade a={L[4].a - 6} b={end(4)}>
        <ScanFocus marks={[{ page: "p15", find: "共产党真是好" }, { page: "p15", find: "这个教训，全党必须记住" }]} at={12} dur={L[4].d - 30} len={len(4, 4)} seed={73} />
      </Fade>
      <Fade a={L[5].a - 6} b={end(5)}>
        <Plate name="muji_maer" len={len(5, 5)} />
      </Fade>
      <Fade a={L[6].a - 6} b={end(7)}>
        <Meeting t7={L[7].a - L[6].a + 6} len={len(6, 7)} />
      </Fade>
      <Fade a={L[8].a - 6} b={end(8)}>
        <Hands len={len(8, 8)} />
      </Fade>
      <Fade a={L[9].a - 6} b={end(9)}>
        <ScanFocus marks={[{ page: "p17", find: "有中央和地方两个积极性，比只有一个积极性好得多" }]} at={40} dur={L[9].d - 70} len={len(9, 9)} seed={75} />
      </Fade>
      <Fade a={L[10].a - 6} b={end(10)}>
        <Measure />
      </Fade>
      <Fade a={L[11].a - 6} b={S.dur}>
        <Trap />
        <Note at={40} label="研读追问" lines={["数字化治理让信息传得更快，", "央地权责的尺度会改变吗？", "激发地方活力的同时，", "如何守住全国统一大市场？"]} x={1150} y={250} w={700} size={44} perLine={44} />
      </Fade>
      {f > c0 - 10 && <RunningHead block="贰 · 利益分配与治理体系" rel={REL[f < L[8].a - 6 ? 0 : 1]} at={c0 - 10} />}
    </AbsoluteFill>
  );
};
