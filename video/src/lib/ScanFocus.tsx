import React, { useMemo } from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import ocrRaw from "../data/ocr.json";
import { C, io, ramp } from "./theme";

type OcrLine = { t: string; box: number[][] };
const OCR = ocrRaw as unknown as Record<string, { size: [number, number]; lines: OcrLine[] }>;
const PW = 1474;
const PH = 2240;
const GAP = 90;

const keep = (ch: string) => /[\u4e00-\u9fffA-Za-z0-9]/.test(ch);

export type Mark = { page: string; find: string; circle?: string };
type Seg = { x0: number; x1: number; y0: number; y1: number };

/** locate `find` (punctuation-insensitive) on a page; returns one segment per covered printed line */
const locate = (page: string, find: string, ox: number): Seg[] => {
  const pg = OCR[page];
  if (!pg) throw new Error(`no OCR for ${page}`);
  const lines = pg.lines.filter((l) => l.t.replace(/[^\u4e00-\u9fff]/g, "").length > 0);
  const map: { li: number; ri: number }[] = [];
  let norm = "";
  lines.forEach((l, li) => {
    [...l.t].forEach((ch, ri) => {
      if (keep(ch)) {
        norm += ch;
        map.push({ li, ri });
      }
    });
  });
  const target = [...find].filter(keep).join("");
  const at = norm.indexOf(target);
  if (at < 0) throw new Error(`"${find}" not found on ${page}`);
  const segs: Seg[] = [];
  for (let k = at; k < at + target.length; k++) {
    const { li, ri } = map[k];
    const l = lines[li];
    const xs = l.box.map((p) => p[0]);
    const ys = l.box.map((p) => p[1]);
    const bx0 = Math.min(...xs);
    const bx1 = Math.max(...xs);
    const n = [...l.t].length;
    const cw = (bx1 - bx0) / n;
    const cx0 = bx0 + cw * ri + ox;
    const last = segs[segs.length - 1] as Seg & { li?: number };
    if (last && (last as { li?: number }).li === li) {
      last.x1 = cx0 + cw;
    } else {
      const s = { x0: cx0, x1: cx0 + cw, y0: Math.min(...ys), y1: Math.max(...ys), li } as Seg & { li: number };
      segs.push(s);
    }
  }
  return segs;
};

const rnd = (seed: number) => {
  let s = seed;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
};

const pencilPath = (x0: number, x1: number, y: number, seed: number) => {
  const r = rnd(seed);
  const pts: string[] = [];
  const n = Math.max(2, Math.round((x1 - x0) / 26));
  for (let i = 0; i <= n; i++) {
    const x = x0 + ((x1 - x0) * i) / n;
    const yy = y + (r() - 0.5) * 3.2 + Math.sin(i / 3) * 0.8;
    pts.push(`${i ? "L" : "M"}${x.toFixed(1)},${yy.toFixed(1)}`);
  }
  return pts.join(" ");
};

export const ScanFocus: React.FC<{
  marks: Mark[];
  pages?: string[];
  /** local frame where the underline starts drawing */
  at?: number;
  /** frames to draw all underlines */
  dur?: number;
  /** total frames this view is on screen (drives the slow push) */
  len?: number;
  w?: number;
  h?: number;
  /** focus centre inside the viewport */
  cy?: number;
  maxScale?: number;
  fitW?: number;
  fitH?: number;
  /** start from a whole-page view and zoom in */
  establish?: boolean;
  dim?: boolean;
  seed?: number;
}> = ({ marks, pages, at = 10, dur = 60, len = 200, w = 1920, h = 1080, cy, maxScale = 1.25, fitW = 1500, fitH = 520, establish = false, dim = true, seed = 7 }) => {
  const f = useCurrentFrame();
  const pageList = pages ?? [...new Set(marks.map((m) => m.page))];
  const offs = (p: string) => pageList.indexOf(p) * (PW + GAP);

  const { segs, circles, bbox } = useMemo(() => {
    const all: (Seg & { mi: number })[] = [];
    const circ: Seg[] = [];
    marks.forEach((m, mi) => {
      locate(m.page, m.find, offs(m.page)).forEach((s) => all.push({ ...s, mi }));
      if (m.circle) {
        const c = locate(m.page, m.circle, offs(m.page));
        circ.push({ x0: Math.min(...c.map((s) => s.x0)), x1: Math.max(...c.map((s) => s.x1)), y0: Math.min(...c.map((s) => s.y0)), y1: Math.max(...c.map((s) => s.y1)) });
      }
    });
    const bb = {
      x0: Math.min(...all.map((s) => s.x0)),
      x1: Math.max(...all.map((s) => s.x1)),
      y0: Math.min(...all.map((s) => s.y0)),
      y1: Math.max(...all.map((s) => s.y1)),
    };
    return { segs: all, circles: circ, bbox: bb };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(marks), JSON.stringify(pageList)]);

  const bw = bbox.x1 - bbox.x0 + 120;
  const bh = bbox.y1 - bbox.y0 + 120;
  const sFocus = Math.min(fitW / bw, fitH / bh, maxScale);
  const centreY = cy ?? h * 0.43;
  const fx = (bbox.x0 + bbox.x1) / 2;
  const fy = (bbox.y0 + bbox.y1) / 2;

  const push = ramp(f, 0, len, 0.93, 1.03, (t) => t);
  let s = sFocus * push;
  let cx = fx;
  let cyW = fy;
  if (establish) {
    const totalW = pageList.length * PW + (pageList.length - 1) * GAP;
    const sPage = Math.min((h * 0.9) / PH, (w * 0.9) / totalW);
    const k = ramp(f, 8, Math.max(at - 4, 40), 0, 1, io);
    s = sPage + (s - sPage) * k;
    cx = totalW / 2 + (fx - totalW / 2) * k;
    cyW = PH / 2 + (fy - PH / 2) * k;
  }
  const tx = w / 2 - cx * s;
  const ty = (establish ? h / 2 + (centreY - h / 2) * ramp(f, 8, Math.max(at - 4, 40), 0, 1, io) : centreY) - cyW * s;

  const lengths = segs.map((sg) => sg.x1 - sg.x0);
  const total = lengths.reduce((a, b) => a + b, 0);
  const prog = ramp(f, at, at + dur, 0, 1, (t) => t) * total;
  const dimK = dim ? ramp(f, at, at + 18) * 0.5 : 0;
  const circK = ramp(f, at + dur, at + dur + 18, 0, 1, io);

  let acc = 0;
  return (
    <AbsoluteFill style={{ width: w, height: h, overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})` }}>
        {pageList.map((p) => (
          <Img
            key={p}
            src={staticFile(`scans/${p}.png`)}
            style={{ position: "absolute", left: offs(p), top: 0, width: PW, height: PH, clipPath: "inset(4.5% 4% 5% 4%)" }}
          />
        ))}
        <svg width={pageList.length * (PW + GAP) + 8000} height={PH + 8000} style={{ position: "absolute", left: -4000, top: -4000 }}>
          <g transform="translate(4000 4000)">
          <defs>
            <filter id={`pc${seed}`} x="-5%" y="-50%" width="110%" height="200%">
              <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} />
              <feDisplacementMap in="SourceGraphic" scale="3.5" />
            </filter>
            <mask id={`dm${seed}`}>
              <rect x={-4000} y={-4000} width={12000} height={12000} fill="white" />
              {segs.map((sg, i) => (
                <rect key={i} x={sg.x0 - 14} y={sg.y0 - 12} width={sg.x1 - sg.x0 + 28} height={sg.y1 - sg.y0 + 30} rx={8} fill="black" />
              ))}
            </mask>
          </defs>
          {dimK > 0 && <rect x={-4000} y={-4000} width={12000} height={12000} fill={C.paper} opacity={dimK} mask={`url(#dm${seed})`} />}
          <g filter={`url(#pc${seed})`} style={{ mixBlendMode: "multiply" }}>
            {segs.map((sg, i) => {
              const start = acc;
              acc += lengths[i];
              const vis = Math.max(0, Math.min(prog - start, lengths[i]));
              if (vis <= 0) return null;
              const y = sg.y1 + 7;
              return (
                <g key={i}>
                  <path d={pencilPath(sg.x0 - 4, sg.x0 - 4 + vis + 6, y, seed + i * 13)} stroke={C.red} strokeWidth={7} strokeLinecap="round" fill="none" opacity={0.82} />
                  <path d={pencilPath(sg.x0, sg.x0 + vis, y + 3, seed + i * 29)} stroke={C.red} strokeWidth={3} strokeLinecap="round" fill="none" opacity={0.5} />
                </g>
              );
            })}
            {circles.map((c, i) => {
              const rx = (c.x1 - c.x0) / 2 + 20;
              const ry = (c.y1 - c.y0) / 2 + 16;
              const cxx = (c.x0 + c.x1) / 2;
              const cyy = (c.y0 + c.y1) / 2;
              const per = 2 * Math.PI * Math.sqrt((rx * rx + ry * ry) / 2) * 1.08;
              return (
                <ellipse
                  key={`c${i}`}
                  cx={cxx}
                  cy={cyy}
                  rx={rx}
                  ry={ry}
                  transform={`rotate(-4 ${cxx} ${cyy})`}
                  stroke={C.red}
                  strokeWidth={6}
                  fill="none"
                  opacity={0.85}
                  strokeDasharray={per}
                  strokeDashoffset={per * (1 - circK)}
                />
              );
            })}
          </g>
          </g>
        </svg>
      </div>
    </AbsoluteFill>
  );
};
