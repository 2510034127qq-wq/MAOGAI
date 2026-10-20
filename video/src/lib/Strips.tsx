import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Mark, ScanFocus } from "./ScanFocus";
import { C, ramp } from "./theme";

/** quotes that run across a page break: one cropped line-strip per mark, stacked */
export const Strips: React.FC<{ items: Mark[]; at?: number; per?: number; w?: number; h?: number; gap?: number; scale?: number; seed?: number }> = ({ items, at = 10, per = 50, w = 1500, h = 150, gap = 40, scale = 1.05, seed = 200 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column", gap, paddingBottom: 90 }}>
      {items.map((m, i) => {
        const a = at + i * per;
        const k = ramp(f, a - 10, a + 10);
        return (
          <div key={i} style={{ position: "relative", width: w, height: h, opacity: k, borderTop: `1px solid ${C.faint}`, borderBottom: `1px solid ${C.faint}` }}>
            <ScanFocus marks={[m]} w={w} h={h} cy={h / 2} at={a} dur={per - 6} len={400} fitW={w - 60} fitH={h + 80} maxScale={scale} dim={false} seed={seed + i} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
