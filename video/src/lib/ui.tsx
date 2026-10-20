import React from "react";
import { AbsoluteFill, Audio, Freeze, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import manifestRaw from "../data/renders.json";
import { C, F, env, io, ramp } from "./theme";
import { TL } from "./timeline";

const manifest = manifestRaw as Record<string, number | string>;
export const hasAsset = (k: string) => !!manifest[k];

/** recorded narration (assets/vo/<lineId>.wav), placed at each line's start */
export const Narration: React.FC = () => (
  <>
    {TL.scenes.flatMap((s) =>
      s.lines.map((l) => {
        const file = manifest[`vo:${(l as { id?: string }).id}`];
        if (typeof file !== "string") return null;
        return (
          <Sequence key={`${s.id}${l.from}`} from={s.from + l.from} durationInFrames={l.to - l.from + 30} layout="none">
            <Audio src={staticFile(`vo/${file}`)} />
          </Sequence>
        );
      }),
    )}
  </>
);

/** global subtitles, driven by timeline.json */
const ALL_SUBS = TL.scenes.flatMap((s) => s.lines.flatMap((l) => l.subs.map((x) => ({ text: x.text, from: x.from + s.from, to: x.to + s.from, q: !!l.q }))));

export const Subtitles: React.FC = () => {
  const f = useCurrentFrame();
  const near = ALL_SUBS.reduce((d, s) => Math.min(d, f < s.from ? s.from - f : f > s.to ? f - s.to : 0), 1e9);
  const band = 1 - Math.min(1, Math.max(0, (near - 8) / 12));
  const cur = ALL_SUBS.find((s) => f >= s.from && f < s.to + 2);
  const backdrop = (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 0,
        height: 230,
        opacity: band,
        background: `linear-gradient(to top, rgba(237,229,212,0.94) 0%, rgba(237,229,212,0.86) 45%, rgba(237,229,212,0) 100%)`,
      }}
    />
  );
  if (!cur) return <AbsoluteFill style={{ pointerEvents: "none" }}>{backdrop}</AbsoluteFill>;
  const o = Math.min(ramp(f, cur.from, cur.from + 4), 1 - ramp(f, cur.to - 1, cur.to + 2));
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 54, pointerEvents: "none" }}>
      {backdrop}
      <div
        style={{
          position: "relative",
          fontFamily: F.serif,
          fontWeight: 600,
          fontSize: 44,
          letterSpacing: 2,
          color: C.ink,
          opacity: o,
          padding: "6px 26px",
          textShadow: `0 0 10px ${C.paper}, 0 0 4px ${C.paper}, 0 0 2px ${C.paper}`,
        }}
      >
        {cur.text}
      </div>
    </AbsoluteFill>
  );
};

/** play a Blender PNG sequence; shows a labelled placeholder until frames exist */
export const FrameSeq: React.FC<{ shot: string; start?: number; rate?: number; style?: React.CSSProperties; hold?: boolean }> = ({ shot, start = 0, rate = 1, style, hold = true }) => {
  const f = useCurrentFrame();
  const n = Number(manifest[shot] ?? 0);
  if (!n) {
    return (
      <AbsoluteFill style={{ backgroundColor: "#2a2621", justifyContent: "center", alignItems: "center", ...style }}>
        <div style={{ fontFamily: F.serif, color: C.faint, fontSize: 40, border: `2px dashed ${C.faint}`, padding: "30px 60px" }}>3D 镜头待渲染：{shot}</div>
      </AbsoluteFill>
    );
  }
  const maxLen = Math.max(1, Math.floor((n - start) / rate));
  const media = <OffthreadVideo src={staticFile(`renders/${shot}.mp4`)} trimBefore={start} playbackRate={rate} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
  return (
    <AbsoluteFill style={style}>
      <Sequence durationInFrames={maxLen} layout="none">
        {media}
      </Sequence>
      {hold && f >= maxLen && (
        <Sequence from={0} layout="none">
          <Freeze frame={n - 1}>
            <OffthreadVideo src={staticFile(`renders/${shot}.mp4`)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          </Freeze>
        </Sequence>
      )}
    </AbsoluteFill>
  );
};

const FadeInner: React.FC<{ len: number; fi: number; fo: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ len, fi, fo, children, style }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ opacity: env(f, 0, len, fi, fo), ...style }}>{children}</AbsoluteFill>;
};

/** a timed layer: children see LOCAL frames (0 = a) */
export const Fade: React.FC<{ a: number; b: number; fi?: number; fo?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ a, b, fi = 14, fo = 14, children, style }) => (
  <Sequence from={a} durationInFrames={Math.max(1, b - a)} premountFor={30}>
    <FadeInner len={b - a} fi={fi} fo={fo} style={style}>
      {children}
    </FadeInner>
  </Sequence>
);

/** text that settles in like ink: blur → sharp, slight rise */
export const Ink: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; d?: number; rise?: number }> = ({ at, children, style, d = 22, rise = 10 }) => {
  const f = useCurrentFrame();
  const k = ramp(f, at, at + d);
  return <div style={{ opacity: k, filter: `blur(${(1 - k) * 6}px)`, translate: `0 ${(1 - k) * rise}px`, ...style }}>{children}</div>;
};

/** handwritten reveal (wipe left→right), for 楷书 margin notes */
export const Write: React.FC<{ at: number; d: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ at, d, children, style }) => {
  const f = useCurrentFrame();
  const k = ramp(f, at, at + d, 0, 1, (t) => t);
  return <div style={{ clipPath: `inset(-20% ${100 - k * 100}% -20% -2%)`, ...style }}>{children}</div>;
};

/** small top-left running head: 壹 · 经济结构与空间布局 / 一 重工业和轻工业、农业的关系 */
export const RunningHead: React.FC<{ block: string; rel?: string; at?: number }> = ({ block, rel, at = 0 }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 84, top: 62, opacity: ramp(f, at, at + 20) * 0.9, fontFamily: F.song, fontSize: 26, color: C.gray, letterSpacing: 4, display: "flex", gap: 22, alignItems: "center" }}>
      <span style={{ color: C.red }}>{block}</span>
      {rel && <span style={{ width: 40, height: 1, background: C.faint }} />}
      {rel && <span>{rel}</span>}
    </div>
  );
};

/** 页边红笔批注 */
export const Note: React.FC<{ at: number; label: string; lines: string[]; x?: number; y?: number; w?: number; size?: number; perLine?: number }> = ({ at, label, lines, x = 1060, y = 230, w = 720, size = 46, perLine = 34 }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w }}>
      <svg width={30} height={lines.length * size * 1.7 + 60} style={{ position: "absolute", left: -48, top: 0, overflow: "visible" }}>
        <path
          d={`M22,4 C6,10 8,30 8,60 L8,${lines.length * size * 1.7} C8,${lines.length * size * 1.7 + 30} 6,${lines.length * size * 1.7 + 50} 22,${lines.length * size * 1.7 + 56}`}
          stroke={C.red}
          strokeWidth={3}
          fill="none"
          strokeDasharray={2000}
          strokeDashoffset={2000 * (1 - ramp(f, at, at + 26, 0, 1, io))}
          opacity={0.85}
        />
      </svg>
      <Ink at={at}>
        <div style={{ fontFamily: F.kai, fontSize: 30, color: C.red, letterSpacing: 6, marginBottom: 14 }}>{label}</div>
      </Ink>
      {lines.map((l, i) => (
        <Write key={i} at={at + 14 + i * perLine} d={perLine}>
          <div style={{ fontFamily: F.kai, fontSize: size, color: C.red, lineHeight: 1.7, opacity: 0.92 }}>{l}</div>
        </Write>
      ))}
    </div>
  );
};

export const ChapterCard: React.FC<{ no: string; title: string; sub: string; items: string; len: number }> = ({ no, title, sub, items, len }) => {
  const f = useCurrentFrame();
  const out = 1 - ramp(f, len - 14, len, 0, 1, io);
  const seal = ramp(f, 4, 22);
  return (
    <AbsoluteFill style={{ opacity: out, justifyContent: "center", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 70 }}>
        <div
          style={{
            width: 210,
            height: 210,
            background: C.red,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            scale: String(1.25 - 0.25 * seal),
            opacity: seal,
            boxShadow: "inset 0 0 18px rgba(60,10,5,0.35)",
            filter: "url(#roughEdge)",
          }}
        >
          <span style={{ fontFamily: F.heavy, fontSize: 150, color: C.paperHi, lineHeight: 1 }}>{no}</span>
        </div>
        <div>
          <Ink at={14}>
            <div style={{ fontFamily: F.heavy, fontSize: 92, color: C.ink, letterSpacing: 10 }}>{title}</div>
          </Ink>
          <Ink at={24}>
            <div style={{ fontFamily: F.song, fontSize: 44, color: C.gray, letterSpacing: 8, marginTop: 18 }}>{sub}</div>
          </Ink>
          <Ink at={34}>
            <div style={{ fontFamily: F.song, fontSize: 30, color: C.red, letterSpacing: 6, marginTop: 30 }}>十大关系之 {items}</div>
          </Ink>
        </div>
      </div>
      <svg width={0} height={0}>
        <filter id="roughEdge">
          <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" seed="3" />
          <feDisplacementMap in="SourceGraphic" scale="6" />
        </filter>
      </svg>
    </AbsoluteFill>
  );
};

/** full-bleed woodcut plate with slow push */
export const Plate: React.FC<{ name: string; len: number; from?: number; to?: number; ox?: [number, number]; oy?: [number, number] }> = ({ name, len, from = 1.04, to = 1.12, ox = [0, 0], oy = [0, 0] }) => {
  const f = useCurrentFrame();
  const t = ramp(f, 0, len, 0, 1, (x) => x);
  if (!manifest[`img:${name}`]) {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ fontFamily: F.serif, color: C.gray, fontSize: 40, border: `2px dashed ${C.faint}`, padding: "30px 60px" }}>木刻插图待生成：{name}</div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(`img/${name}_paper.png`)}
        style={{ width: "100%", height: "100%", objectFit: "cover", scale: String(from + (to - from) * t), translate: `${ox[0] + (ox[1] - ox[0]) * t}px ${oy[0] + (oy[1] - oy[0]) * t}px` }}
      />
    </AbsoluteFill>
  );
};

export const useFps = () => useVideoConfig().fps;
