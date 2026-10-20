import timeline from "../data/timeline.json";

export type Sub = { text: string; from: number; to: number };
export type Line = { t: string; q?: number; ask?: number; v?: string; from: number; to: number; subs: Sub[] };
export type Card = { no: string; title: string; sub: string; items: string };
export type SceneData = { id: string; name: string; from: number; dur: number; card?: Card | null; lines: Line[] };

export const TL = timeline as unknown as { fps: number; total: number; scenes: SceneData[] };

export const scene = (id: string): SceneData => {
  const s = TL.scenes.find((x) => x.id === id);
  if (!s) throw new Error(`scene ${id} missing`);
  return s;
};

/** beat helper: start/end frame of line i within a scene, with optional offsets */
export const beats = (s: SceneData) => (i: number) => {
  const l = s.lines[i];
  if (!l) throw new Error(`${s.id} line ${i} missing`);
  return { a: l.from, b: l.to, d: l.to - l.from, next: s.lines[i + 1]?.from ?? s.dur };
};
