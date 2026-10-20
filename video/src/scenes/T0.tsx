import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { C, F, io, ramp } from "../lib/theme";
import { scene } from "../lib/timeline";
import { FrameSeq, Ink } from "../lib/ui";

const S = scene("T0");

export const T0: React.FC = () => {
  const f = useCurrentFrame();
  const cut = 150;
  const paper = ramp(f, cut - 16, cut + 6, 0, 1, io);
  const press = ramp(f, cut, cut + 26);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: ramp(f, 0, 14) }}>
        <FrameSeq shot="leadtype_title" />
      </AbsoluteFill>
      <AbsoluteFill style={{ opacity: paper }}>
        <Img src={staticFile("tex/paper.jpg")} style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      {f >= cut - 4 && (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
          <Ink at={cut + 26} d={20}>
            <div style={{ fontFamily: F.song, fontSize: 30, color: C.red, letterSpacing: 10, marginBottom: 46 }}>一九五六 · 四 · 二十五　—　二〇二六</div>
          </Ink>
          <div
            style={{
              fontFamily: F.heavy,
              fontSize: 138,
              letterSpacing: 26,
              color: C.ink,
              opacity: press,
              scale: String(1.06 - 0.06 * press),
              filter: `blur(${(1 - press) * 5}px)`,
              textShadow: "0 0 1px rgba(28,26,23,0.5)",
            }}
          >
            破立并举<span style={{ display: "inline-block", width: 70 }} />统筹兼顾
          </div>
          <svg width={900} height={30} style={{ marginTop: 26 }}>
            <line x1={450 - 440 * ramp(f, cut + 18, cut + 50, 0, 1, io)} x2={450 + 440 * ramp(f, cut + 18, cut + 50, 0, 1, io)} y1={15} y2={15} stroke={C.red} strokeWidth={3} />
          </svg>
          <Ink at={cut + 34} d={24}>
            <div style={{ fontFamily: F.song, fontSize: 52, color: C.gray, letterSpacing: 12, marginTop: 24 }}>研读毛泽东《论十大关系》</div>
          </Ink>
        </AbsoluteFill>
      )}
      <AbsoluteFill style={{ backgroundColor: C.paper, opacity: ramp(f, S.dur - 12, S.dur) }} />
    </AbsoluteFill>
  );
};
